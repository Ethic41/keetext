#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-18 03:07:01
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

from core.requester.requester import Requester
from bs4 import BeautifulSoup as bs
import core.amazon_scraper.constants as const
from core.amazon_scraper.structures import Category, CategoryList, SubCategory, SubCategoryList, ProductList, Product, SoupType, SoupTag
from core.writer.writer import Writer
import hashlib
import re


class Scraper:
    def __init__(self):
        self.base_url = const.base_url
        self.requester = Requester()
        self.writer = Writer()
        self.requester.make_request(self.base_url)
        self.categories: CategoryList = []  # take care in adding and removing items
        self.subcategories: SubCategoryList = []  # appropriately to save memory
        self.retrieved_products: ProductList = []  # this will contain retrieved items_data, size not > 10
        self.retrieved_products_count: int = 0
        self.total_retrieved_product_count: int = 0
        self.started = False
        self.stopped = False
        self.ready_status = "Ready..."
        self.stopped_status = "Scraping Stopped!"
        self.stopping_status = "Stopping..."
        self.scraping_status = "Scraping Started..."
        self.completed_subcategory = "Moving to next Subcategory..."
        self.completed_status = "Scraping Completed Successfully..."
        self.scrape_status = self.ready_status
    
    def set_categories(self, categories_soup)->CategoryList:
        self.categories: CategoryList = []
        for category_link in categories_soup.find_all(const.categories_tag, const.categories_attributes):
            category = Category()
            category.category_id = category_link[const.categories_id_name]
            category.category_name = str(category_link.div.string).strip()
            self.categories.append(category)
    
    def set_subcategories(self, categories: CategoryList, categories_soup)->SubCategoryList:
        self.subcategories: SubCategoryList = []
        for category in categories:
            const.subcat_grp_attributes[const.categories_id_name] = category.category_id
            subcat_grp = categories_soup.find(const.subcat_grp_tag, const.subcat_grp_attributes)
            for subcat_item in subcat_grp.find_all(const.subcat_tag, const.subcat_attributes):
                subcategory: SubCategory = SubCategory()
                subcategory.url = subcat_item["href"]
                subcategory.valid_url = subcategory.url
                subcategory.name = str(subcat_item.div.string).strip()
                subcategory.url_hash = hashlib.sha1(str(subcategory.url).encode("utf8")).hexdigest()
                subcategory.category_id = category.category_id
                subcategory.category_name = category.category_name
                self.subcategories.append(subcategory)

    def set_categories_and_subcategories(self):
        soup = self.make_soup(self.base_url + const.get_categories_url, payload=const.get_categories_payload)
        self.set_categories(soup)
        self.set_subcategories(self.categories, soup)
    
    def make_soup(self, url: str, payload=None)->SoupType:
        content = self.requester.make_request(url, payload=payload)
        return bs(content, const.parser)
    
    def filter_by_rating(self, rating: int):
        self.scrape_status = f"filtering {rating}-Star Rated Products..."
        for subcategory in self.subcategories:
            try:
                if (subcategory.selected) and (subcategory.validity == const.valid):
                    soup = self.make_soup(self.base_url + subcategory.valid_url)
                    star_rating_attributes = const.ratings[rating]

                    star_rating_section_tag: SoupTag = soup.find(const.star_tag, attrs=star_rating_attributes)
                    if (star_rating_section_tag) and (star_rating_section_tag.parent.name == "a"):
                        subcategory.valid_url = star_rating_section_tag.parent["href"]
                    else:
                        subcategory.validity = const.invalid
            except Exception:
                continue
    
    def filter_by_include_not_available(self):
        self.scrape_status = "filtering not available Products..."
        for subcategory in self.subcategories:
            try:
                if (subcategory.selected) and (subcategory.validity == const.valid):
                    soup = self.make_soup(self.base_url + subcategory.valid_url)

                    not_available_section_tag: SoupTag = soup.find(const.not_avail_section_tag, attrs=const.not_avail_section_attributes)
                    if (not_available_section_tag) and (not_available_section_tag.a):
                        subcategory.valid_url = not_available_section_tag.a["href"]
                    else:
                        subcategory.validity = const.invalid
            except Exception:
                continue
    
    def retrieve_not_available_item(self, output_file_format, output_dir, min_rank=None, max_rank=None, min_subrank=None, max_subrank=None):
        self.writer.create_file(output_file_format, output_dir)   # create the excel file in memory
        self.scrape_status = self.scraping_status
        for subcategory in self.subcategories:
            try:
                if (subcategory.selected) and (subcategory.validity == const.valid):
                    # confirming item is selected and valid
                    while(subcategory.valid_url):
                        if (self.started == False) and (self.stopped == True):
                            self.stop()
                        soup = self.make_soup(self.base_url + subcategory.valid_url)
                        if soup.find(string=const.not_available_string):   # the page contain not available product
                            # for each product in the page, we are trying to find matching product
                            for product_section in soup.find_all(const.item_section_tag, const.item_section_attributes):
                                product_section: SoupTag = product_section
                                # if this is the matching product
                                if product_section.find(string=const.not_available_string):
                                    new_product: Product = Product()
                                    new_product.product_url = product_section.a["href"]
                                    product_information = self.extract_product_information(new_product.product_url)

                                    if min_rank and max_rank:
                                        if not self.is_valid_rank(product_information, min_rank, max_rank):
                                            continue

                                    if min_subrank and max_subrank:
                                        if not self.is_valid_subrank(product_information, min_subrank, max_subrank):
                                            continue

                                    if (self.retrieved_products_count < 10) and (product_information):
                                        product_information["category"] = subcategory.category_name
                                        product_information["subcategory"] = subcategory.name
                                        new_product.product_data = product_information
                                        self.retrieved_products.append(new_product)
                                        self.retrieved_products_count += 1
                                        self.total_retrieved_product_count += 1
                                        self.show_product_count()
                                    
                                    elif product_information:
                                        product_information["category"] = subcategory.category_name
                                        product_information["subcategory"] = subcategory.name
                                        new_product.product_data = product_information
                                        self.total_retrieved_product_count += 1
                                        self.show_product_count()
                                        self.retrieved_products.append(new_product)

                                        self.writer.write(self.retrieved_products)
                                        
                                        self.retrieved_products: ProductList = []
                                        self.retrieved_products_count: int = 0

                                        if (self.started == False) and (self.stopped == True):
                                            self.stop()

                                        # retrieve item is upto 10 we need write data
                                else:
                                    continue
                            subcategory.valid_url = self.get_next_page_link(soup)
                            continue
                        else:   # the does not contain not available item, we retrieve next page
                            subcategory.valid_url = self.get_next_page_link(soup)

                    self.write_and_cleanup()   #  finish writing whatever is left
                    self.scrape_status = self.completed_subcategory    # completed scraping
            except KeyboardInterrupt:
                self.write_and_cleanup()
            except Exception as e:
                self.write_and_cleanup()
                print(e)
                continue
        self.scrape_status = self.completed_status

    def show_product_count(self):
        self.scrape_status = f"Retrieved {self.total_retrieved_product_count} matching Products"
    
    def stop(self):
        self.scrape_status = self.stopping_status
        raise KeyboardInterrupt

    def write_and_cleanup(self):
        self.writer.write(self.retrieved_products)
        self.writer.close_workbook()
        self.retrieved_products: ProductList = []
        self.retrieved_products_count: int = 0
        self.total_retrieved_product_count: int = 0
        self.scrape_status = self.stopped_status

    def extract_product_information(self, url: str)->dict:
        product_information = {}
        labels = []
        values = []
        soup = self.make_soup(self.base_url + url)

        if soup.find(const.product_tag, const.product_label_attributes):
            for item_label_tag in soup.find_all(const.product_tag, const.product_label_attributes):
                labels.append(str(item_label_tag.string).strip("\n").strip())
        else:
            return {}
        
        if soup.find(const.product_tag, const.product_value_attributes):
            for item_value_tag in soup.find_all(const.product_tag, const.product_value_attributes):
                values.append(str(item_value_tag.string).strip("\n").strip())
        else:
            return {}
        
        number_of_product_info = min(len(labels), len(values))
        for i in range(number_of_product_info):
            try:
                if values[i] != "None":
                    product_information[labels[i]] = values[i]
            except Exception:
                continue
        
        ranks = soup.find_all(string=const.rank_pattern)
        try:
            if len(ranks) > 0:
                rank = re.search(const.num_pattern, ranks[0]).group(0)
                product_information["rank"] = rank
            if len(ranks) > 1:
                subrank = re.search(const.num_pattern, ranks[1]).group(0)
                product_information["subrank"] = subrank
        except Exception:
            pass
    
        
        product_information["product_url"] = self.base_url + url

        return product_information

    def get_next_page_link(self, page_soup: SoupTag)->str:
        tag = page_soup.find(const.next_page_tag, attrs=const.next_page_attributes)
        try:
            if tag.a:
                return tag.a["href"]
        except Exception:
            pass
        
        return None

    def is_valid_rank(self, product: dict, min_rank: int, max_rank: int):
        try:
            rank = product["rank"]
            rank = int(rank.replace(".", ""))
            return (min_rank <= rank <= max_rank)
        except KeyError:
            return False

    def is_valid_subrank(self, product: dict, min_subrank, max_subrank):
        try:
            subrank = product["subrank"]
            subrank = int(subrank.replace(".", ""))
            return (min_subrank <= subrank <= max_subrank)
        except KeyError:
            return False
        
        


