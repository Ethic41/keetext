#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-21 01:05:33
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)


from typing import List, Dict, NewType, Deque
from bs4 import BeautifulSoup as bs
from PyQt5 import QtWidgets
from bs4.element import Tag

class Category:
    def __init__(self):
        pass

    category_id: str = None
    category_name: str = None
    selected: bool = False
    subcat_displayed: bool = False

class SubCategory(Category):
    def __init__(self):
        pass

    name: str = None
    url: str = None
    url_hash: str = None
    valid_url: str = None
    validity: str = "valid"
    next_valid_url: str = None
    selected: bool = False

class SearchSubCategory(SubCategory):
    def __init__(self):
        pass


ItemData = Dict[str, str]

class Product:
    def __init__(self):
        pass
    
    product_url = None
    product_data: ItemData = {}

SoupType = NewType("SoupType", bs)
SoupTag = NewType("SoupTag", Tag)
ListWidgetItem = NewType("ListWidgetItem", QtWidgets.QListWidgetItem)
ProductList = List[Product]
UnretrievedProductList = Deque[Product]
CategoryList = List[Category]
SearchSubCategoryList = Deque[SearchSubCategory]
SubCategoryList = List[SubCategory]


if __name__=="__main__":
    pass