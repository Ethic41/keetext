#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-18 03:08:52
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

import re

# TODO: implemet the get_base_url from GUI
base_url = r"https://www.amazon.de"
# base_url = r"http://localhost:8080"
get_categories_url = r"/gp/navigation/ajax/generic.html"
#get_categories_url = r"/clean.html"
get_categories_payload = {"ajaxTemplate":"hamburger", "hmDataAjaxHint":"1"}
categories_tag = "a"
categories_attributes = {"class":"hmenu-item", "data-menu-id":re.compile(r"\d+"), "href":""}
categories_id_name = "data-menu-id"
subcat_grp_tag = "ul"
subcat_grp_attributes = {"class":["hmenu", "hmenu-translateX-right", "hmenu-hidden"], "data-parent-menu-id": re.compile(r"\d+"), categories_id_name:""}
subcat_tag = "a"
subcat_attributes = {"class":"hmenu-item", "href":re.compile(r".{3,}")}

# star ranking retrieval constants
star_tag = "i"
one_star_attributes = {"class":"a-star-medium-1"}
two_star_attributes = {"class":"a-star-medium-2"}
three_star_attributes = {"class":"a-star-medium-3"}
four_star_attributes = {"class":"a-star-medium-4"}
ratings = {1: one_star_attributes, 2: two_star_attributes, 3: three_star_attributes, 4: four_star_attributes}

# not available section retrieval constants
not_avail_section_tag = "ul"
not_avail_section_attributes = {"aria-labelledby":"p_n_availability-title"}

# pagination section retrieval constants
pagination_section_tag = "ul"
pagination_section_attributes = {"class":"a-pagination"}
next_page_tag = "li"
next_page_attributes = {"class":"a-last"}

# item section retrieval constants
# Usu_p you are right...we really don't forget this stuff...it's all there....in our Big heads

not_available_string = re.compile(r"Derzeit nicht auf Lager\.|Derzeit nicht verfügbar\.|Currently not on stock\.|Currently unavailable\.|Momentan nicht verfügbar\.|unavailable")
uuid_pattern = re.compile(r"[a-z0-9\-]{36}")
asin_pattern = re.compile(r"[A-Z0-9]{10}")
index_pattern = re.compile(r"\d+")
item_section_tag = "div"
item_section_attributes = {"data-asin":asin_pattern, "data-uuid":uuid_pattern, "data-index":index_pattern}
product_url_tag = "a"
product_url_attributes = {"class": "a-link-normal"}
product_tag = "td"
product_label_attributes = {"class":"label"}
product_value_attributes = {"class":"value"}
rank_pattern = re.compile(r"Nr\. \d+")
num_pattern = re.compile(r"\d{1,}\.{0,}\d{0,}")

# class strings
invalid = "invalid"
valid = "valid"
parser = "lxml"

# search section
departments_tag = "div"
departments_attributes = {"id": "departments"}
department_section_tag = "li"
department_section_attributes = {"id": re.compile(r"n/\d+")}