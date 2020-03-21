#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-18 03:07:01
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

# from core.amazon_scraper.constants import *
from core.requester.reqester import Requester
from bs4 import BeautifulSoup as bs
import core.amazon_scraper.constants as const
from core.amazon_scraper.structures import Category, CategoryList, SubCategory, SubCategoryList, ItemData, Item, ItemList, SoupType
import hashlib


class Scraper:
    def __init__(self):
        self.base_url = const.base_url
        self.requester = Requester()
        self.requester.make_request(self.base_url)
        self.chosen_categories: CategoryList = []  # take care in adding and removing items
        self.chosen_subcategories: SubCategoryList = []  # appropriately to save memory
        self.retrieved_items: ItemList = []  # this will contain retrieved items_data, size not > 10
        self.retrieved_item_count: int = 0
    
    def get_categories(self, categories_soup)->CategoryList:
        categories: CategoryList = []   # structure: {catgry_id: catgry_name}
        for category_link in categories_soup.find_all(const.categories_tag, const.categories_attributes):
            category = Category()
            category.category_id = category_link[const.categories_id_name]
            category.category_name = str(category_link.div.string).strip()
            categories.append(category)
        return categories
    
    def get_subcategories(self, categories: CategoryList, categories_soup)->SubCategoryList:
        subcategories: SubCategoryList = []  # structure: {catgry_id: {subcat_url_hash: (subcat_url, subcat_name)}}
        for category in categories:
            const.subcat_grp_attributes[const.categories_id_name] = category.category_id
            subcat_grp = categories_soup.find(const.subcat_grp_tag, const.subcat_grp_attributes)
            for subcat_item in subcat_grp.find_all(const.subcat_tag, const.subcat_attributes):
                subcategory: SubCategory = SubCategory()
                subcategory.url = subcat_item["href"]
                subcategory.name = str(subcat_item.div.string).strip()
                subcategory.url_hash = hashlib.sha1(str(subcategory.url).encode("utf8")).hexdigest()
                subcategory.category_id = category.category_id
                subcategory.category_name = category.category_name
                subcategories.append(subcategory)
        return subcategories

    def make_categories_soup(self):  # TODO: move to make_soup later
        categories_request = self.requester.make_request(self.base_url + const.get_categories_url, payload=const.get_categories_payload)
        return bs(categories_request, const.parser)  # return a soup object for categories
    
    def make_soup(self, url: str, payload=None)->SoupType:
        content = self.requester.make_request(url, payload=payload)
        return bs(content, const.parser)


    def get_not_available_subcategory_page(self, selected_star_rating: int):
        for selected_subcategory in self.chosen_subcategories:
            try:
                subcategory_page_request = self.requester.make_request(self.base_url + selected_subcategory.url)
                soup = bs(subcategory_page_request, const.parser)
                if selected_star_rating == 1:
                    star_rating = const.one_star_attributes
                elif selected_star_rating == 2:
                    star_rating = const.two_star_attributes
                elif selected_star_rating == 4:
                    star_rating = const.four_star_attributes
                else:
                    star_rating = const.three_star_attributes
            
                star_rating_tag = soup.find(const.star_tag, attrs=star_rating)
                if star_rating_tag:   # checking if this is not None
                    if star_rating_tag.parent.name == "a":   # unless the parent tag is "a", invalid tag
                        url = star_rating_tag.parent["href"]
                        try:
                            not_available_page_request = self.requester.make_request(self.base_url + url)
                            soup = bs(not_available_page_request, const.parser)
                            not_available_tag = soup.find(const.not_avail_section_tag, const.not_avail_section_attributes)
                            if not_available_tag:
                                if not_available_tag.a:
                                    not_available_url = not_available_tag.a["href"]
                                    selected_subcategory.final_valid_url = not_available_url
                                    selected_subcategory.validity = const.valid
                                else:
                                    selected_subcategory.validity = const.invalid
                            else:
                                selected_subcategory.validity = const.invalid
                        except Exception:
                            continue
                    else:
                        selected_subcategory.validity = const.invalid
                else:
                    selected_subcategory.validity = const.invalid
            except Exception:
                continue

    def retrieve_out_of_stock_items(self):
        for selected_subcategory in self.chosen_subcategories:
            if selected_subcategory.validity == const.valid:
                current_items_page = self.make_soup(self.base_url + selected_subcategory.final_valid_url)
                next_page_section = current_items_page.find(const.pagination_section_tag)

