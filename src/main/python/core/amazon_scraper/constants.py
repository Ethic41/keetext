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
categories_tag_name = "a"
categories_attributes = {"class":"hmenu-item", "data-menu-id":re.compile(r"\d+"), "href":""}
categories_id_name = "data-menu-id"
subcat_grp_tag = "ul"
subcat_grp_attributes = {"class":["hmenu", "hmenu-translateX-right", "hmenu-hidden"], "data-parent-menu-id": re.compile(r"\d+"), categories_id_name:""}
subcat_tag_name = "a"
subcat_attributes = {"class":"hmenu-item", "href":re.compile(r".{3,}")}


