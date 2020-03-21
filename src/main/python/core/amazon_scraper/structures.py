#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-21 01:05:33
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
from typing import List, Dict, NewType
from bs4 import BeautifulSoup as bs

class Category:
    def __init__(self):
        pass

    category_id: str = None
    category_name: str = None

class SubCategory(Category):
    def __init__(self):
        pass

    name: str = None
    url: str = None
    url_hash: str = None
    final_valid_url: str = None
    validity: str = None
    next_valid_url: str = None

ItemData = Dict[str, str]

class Item:
    def __init__(self):
        pass

    item_data: ItemData = {}

SoupType = NewType("Soup", bs)
ItemList = List[Item]
CategoryList = List[Category]
SubCategoryList = List[SubCategory]


if __name__=="__main__":
    pass