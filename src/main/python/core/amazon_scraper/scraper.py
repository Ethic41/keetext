#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-18 03:07:01
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

from core.requester.requester import Requester
from bs4 import BeautifulSoup as bs
import core.amazon_scraper.constants as const
from core.amazon_scraper.structures import Category, CategoryList, SubCategory, SubCategoryList, ProductList, Product, SoupType, SoupTag, SearchSubCategory, SearchSubCategoryList, UnretrievedProductList
from core.writer.writer import Writer
from collections import deque
from time import sleep
from threading import Thread
import threading
import hashlib
import re


class Scraper:
    def __init__(self):
        self.base_url = const.base_url
        self.requester = Requester()
        # self.writer = Writer()
        self.requester.make_request(self.base_url)
        self.categories: CategoryList = []  # take care in adding and removing items
        self.subcategories: SubCategoryList = []  # appropriately to save memory
        self.retrieved_products: ProductList = []  # this will contain retrieved items_data, size not > 10
        # self.unrated_subcategories: SearchSubCategoryList = deque()  # this will contain categories found during search
        # self.rated_subcategories: SearchSubCategoryList = deque()
        # self.fully_filtered_subcategories: SearchSubCategoryList = deque()  # all user define filters have been added
        # self.unretrieved_products: UnretrievedProductList = deque()
        # self.retrieved_search_product: UnretrievedProductList = deque()
        
        self.retrieved_products_count: int = 0
        self.total_retrieved_product_count: int = 0
        self.retrieved_search_product_count: int = 0
        self.started = False
        self.stopped = False
        self.started_search = False
        self.stopped_search = False
        self.ready_status = "Ready..."
        self.stopped_status = "Scraping Stopped!"
        self.searching_stopped_status = "Searching Stopped!"
        self.stopping_status = "Stopping..."
        self.scraping_status = "Scraping Started..."
        self.searching_status = "Searching Started..."
        self.completed_subcategory = "Moving to next Subcategory..."
        self.completed_status = "Scraping Completed Successfully..."
        self.search_completed_status = "Searching Completed Successfully..."
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
        self.writer = Writer()
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
        if self.started and not self.stopped:   # this means we completed the task wthout being stopped
            self.scrape_status = self.completed_status
        if self.stopped and not self.started:   # this means program was stopped
            self.scrape_status = self.stopped_status

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

    def search(self, search_term: str):
        self.all_search_subcategories_retrieved = False  # we haven't retrieved all subcategories
        self.retrieved_search_product_count = 0
        self.unrated_subcategories: SearchSubCategoryList = deque()  # TODO: remove the declaration from init
        self.scrape_status = self.searching_status
        soup: SoupType = self.make_soup(self.base_url + const.search_path, payload={const.search_param: search_term})

        self.scrape_status = "Retrieving search subcategories..."
        departments_section: SoupTag = soup.find(const.departments_tag, const.departments_attributes)
        if departments_section:
            for department_section in departments_section.find_all(const.department_section_tag, const.department_section_attributes):
                if department_section:
                    search_subcategory: SearchSubCategory = SearchSubCategory()
                    search_subcategory.url = department_section.a["href"]
                    search_subcategory.valid_url = search_subcategory.url
                    self.unrated_subcategories.appendleft(search_subcategory)
            
            self.all_search_subcategories_retrieved = True   # we have retrieved all subcats
            
    
    def apply_rating_filter_to_search(self, rating: int, finder: Thread):
        main_thread = threading.main_thread()
        self.rated_subcategories: SearchSubCategoryList = deque()

        while True:
            if not main_thread.is_alive():
                exit(0)

            if self.search_has_been_stopped():
                self.scrape_status = self.searching_stopped_status
                exit(0)

            if not finder.is_alive() and not self.unrated_subcategories:
                exit(0)

            try:
                if self.unrated_subcategories:
                    self.scrape_status = f"filtering {rating}-Star Rated Searched Products..."
                    search_subcategory = self.unrated_subcategories.pop()
                
                    if search_subcategory.validity == const.valid:
                        soup = self.make_soup(self.base_url + search_subcategory.valid_url)
                        star_rating_attributes = const.ratings[rating]

                        star_rating_section_tag: SoupTag = soup.find(const.star_tag, attrs=star_rating_attributes)
                        if (star_rating_section_tag) and (star_rating_section_tag.parent.parent.name == "a"):
                            search_subcategory.valid_url = star_rating_section_tag.parent.parent["href"]
                            self.rated_subcategories.appendleft(search_subcategory)
                        else:
                            del search_subcategory
            except Exception:
                continue 
    
    def apply_include_not_available_filter_to_search(self, workers_1):
        self.fully_filtered_subcategories: SearchSubCategoryList = deque()  # all user define filters have been added

        main_thread = threading.main_thread()
        while True:
            if not main_thread.is_alive():
                exit(0)
            
            if self.search_has_been_stopped():
                self.scrape_status = self.searching_stopped_status
                exit(0)
            
            if not self.rated_subcategories and self.workers_are_dead(workers_1):
                exit(0)
            
            try:
                if self.rated_subcategories:
                    self.scrape_status = "filtering not available Searched Products..."
                    search_subcategory = self.rated_subcategories.pop()

                    if search_subcategory.validity == const.valid:
                        soup = self.make_soup(self.base_url + search_subcategory.valid_url)

                        not_available_section_tag: SoupTag = soup.find(const.not_avail_section_tag, attrs=const.not_avail_section_attributes)
                        if (not_available_section_tag) and (not_available_section_tag.a):
                            search_subcategory.valid_url = not_available_section_tag.a["href"]
                            self.fully_filtered_subcategories.appendleft(search_subcategory)
                        else:
                            del search_subcategory
            except Exception:
                continue
    
    def retrieve_product_url(self, workers_2):
        main_thread = threading.main_thread()
        self.unretrieved_products: UnretrievedProductList = deque()

        while True:
            if not main_thread.is_alive():
                exit(0)
            
            if self.search_has_been_stopped():
                self.scrape_status = self.searching_stopped_status
                exit(0)
            
            if not self.fully_filtered_subcategories and self.workers_are_dead(workers_2):
                exit(0)

            try:
                if self.fully_filtered_subcategories:
                    search_subcategory = self.fully_filtered_subcategories.pop()
                    if search_subcategory.validity == const.valid:
                        while(search_subcategory.valid_url):
                            self.scrape_status = "Retrieving products page address..."
                            if self.search_has_been_stopped():
                                self.scrape_status = self.searching_stopped_status
                                exit(0)

                            soup = self.make_soup(self.base_url + search_subcategory.valid_url)
                            if soup.find(string=const.not_available_string):   # the page contain not available product
                                # for each product in the page, we are trying to find matching product
                                for product_section in soup.find_all(const.item_section_tag, const.item_section_attributes):
                                    self.scrape_status = "Retrieving products page address..."
                                    product_section: SoupTag = product_section
                                    # if this is the matching product
                                    if product_section.find(string=const.not_available_string):
                                        new_product: Product = Product()
                                        new_product.product_url = product_section.a["href"]
                                        self.unretrieved_products.appendleft(new_product)
                                
                                search_subcategory.valid_url = self.get_next_page_link(soup)
                                continue       
                            else:   # the does not contain not available item, we retrieve next page
                                search_subcategory.valid_url = self.get_next_page_link(soup)
            except Exception:
                continue
    
    def retrieve_product(self, workers_3, min_rank=None, max_rank=None, min_subrank=None, max_subrank=None):
        self.retrieved_search_product: UnretrievedProductList = deque()
        main_thread = threading.main_thread()

        while True:
            if not main_thread.is_alive():
                exit(0)
            
            if self.search_has_been_stopped():
                self.scrape_status = self.searching_stopped_status
                exit(0)
            
            if not self.unretrieved_products and self.workers_are_dead(workers_3):
                exit(0)
            
            if self.unretrieved_products:
                self.scrape_status = "Retrieving product..."
                try:
                    product: Product = self.unretrieved_products.pop()
                    product_information = self.extract_product_information(product.product_url)

                    if min_rank and max_rank:
                        if not self.is_valid_rank(product_information, min_rank, max_rank):
                            continue

                    if min_subrank and max_subrank:
                        if not self.is_valid_subrank(product_information, min_subrank, max_subrank):
                            continue
                    
                    product.product_data = product_information
                    self.retrieved_search_product.appendleft(product)
                    self.retrieved_search_product_count += 1
                    self.show_searched_product_count()

                except Exception as e:
                    print(e)
            else:
                pass
    
    def search_cleanup(self):
        self.retrieved_search_product_count = 0
        self.retrieved_search_product: UnretrievedProductList = deque()
        self.unretrieved_products: UnretrievedProductList = deque()
        exit(0)
    
    def search_has_been_stopped(self):
        return self.stopped_search and not self.started_search
    
    def search_has_not_been_stopped(self):
        return self.started_search and not self.stopped_search
    
    def workers_are_dead(self, workers: list):
        for worker in workers:
            if worker.is_alive():
                return False
        
        return True
    
    def write_retrieved_product(self, output_dir, workers_4):
        output_file_format = "all"
        self.writer = Writer()
        self.writer.create_file(output_file_format, output_dir)   # create the excel file in memory

        main_thread = threading.main_thread()

        while main_thread.is_alive():
            try:
                if self.search_has_been_stopped():
                    self.writer.close_workbook()
                    self.search_cleanup()
                
                if not self.retrieved_search_product and self.workers_are_dead(workers_4):
                    self.scrape_status = f"Search Completed successfully, {self.retrieved_search_product_count} retrieved"
                    self.writer.close_workbook()
                    self.search_cleanup()

                self.show_searched_product_count()
                
                if self.retrieved_search_product:
                    product = self.retrieved_search_product.pop()
                    self.writer.write([product])
                    self.show_searched_product_count()
            except Exception:
                continue
        
        self.writer.close_workbook()
        self.search_cleanup()
    

    def show_searched_product_count(self):
        self.scrape_status = f"Retrieved {self.retrieved_search_product_count} matching Products"
        
