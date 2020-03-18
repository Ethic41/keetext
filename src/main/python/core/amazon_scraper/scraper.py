#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-18 03:07:01
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

from core.amazon_scraper.constants import *
from core.requester.reqester import Requester
from bs4 import BeautifulSoup as bs

# TODO: take care of this wild-card-bullshit
re.compile("")

class Scraper:
    def __init__(self):
        self.requester = Requester()
        self.requester.make_request(base_url)
    
    def get_categories(self, categories_soup)->dict:
        categories = {}   # structure: {catgry_id: catgry_name}
        for category_link in categories_soup.find_all(categories_tag_name, categories_attributes):
            category_id = category_link[categories_id_name]
            category_name = str(category_link.div.string).strip()
            categories[category_id] = category_name
        return categories
    
    def get_subcategories(self, categories: dict, categories_soup)->dict:
        subcategories = {}   # structure: {catgry_id: {subcat_url: subcat_name}}
        for category_id in categories:
            subcat_grp_attributes[categories_id_name] = category_id
            subcat_grp = categories_soup.find(subcat_grp_tag, subcat_grp_attributes)
            for subcat_item in subcat_grp.find_all(subcat_tag_name, subcat_attributes):
                subcat_url = subcat_item.a["href"]
                subcat_name = str(subcat_item.a.div.string).strip()
                subcategories[category_id] = {subcat_url: subcat_name}
        return subcategories

    def make_categories_soup(self):
        categories_request = self.requester.make_request(get_categories_url, payload=get_categories_payload)
        return bs(categories_request.content, "lxml")  # return a soup object for categories

