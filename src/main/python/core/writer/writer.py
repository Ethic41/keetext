#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-24 15:37:25
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

import xlsxwriter as xl
from core.amazon_scraper.structures import Product, ProductList
import time


class Writer:

    def __init__(self):
        self.extension = ".xlsx"
        self.workbook = None
        self.current_worksheet = None
        self.current_filename = None
        self.output_file_format = None
        self.current_category = None
        self.current_subcategory = None
        self.current_data_fields = []
        self.current_row = 1
    
    def create_workbook(self):
        self.workbook = xl.Workbook(self.current_filename)  # write_only=True
    
    def create_worksheet(self, name=None):
        self.current_worksheet = self.workbook.add_worksheet(name=name)
    
    def add_data(self, row, column, data):
        print("appending!!")
        self.current_worksheet.write_row(row, column, [data])
    
    def close_workbook(self):
        self.workbook.close()
        self.workbook = None
        self.current_worksheet = None
        self.current_filename = None
        self.output_file_format = None
        self.current_category = None
        self.current_subcategory = None
        self.current_data_fields = []
        self.current_row = 1
        # self.current_col = 0

    def create_file(self, output_file_format, output_dir):
        self.set_file_name(output_file_format, output_dir)  # create filename
        self.create_workbook()
        self.create_worksheet()
        self.output_file_format = output_file_format
    
    def write(self, products: ProductList):
        for product in products:
            product: Product = product
            self.create_fields(product.product_data.keys())
            
            if self.output_file_format == "all":
                self.output_all_in_one(product)
            elif self.output_file_format == "category":
                self.output_by_category(product)
            else:
                self.output_by_subcategory(product)
    
    def create_fields(self, field_list: list):
        for field in field_list:
            try:
                self.current_data_fields.index(field)
            except Exception:
                print("appending!!!")
                self.current_data_fields.append(field)
                index = self.current_data_fields.index(field)
                self.add_data(0, index, field)

    def output_all_in_one(self, product: Product):
        indices = self.get_indices(product.product_data.keys())
        values = product.product_data.values()
        self.append_product(indices, values)

    def output_by_category(self, product: Product):
        pass

    def output_by_subcategory(self, product: Product):
        pass

    def get_indices(self, fields_list: list):
        indices = []
        for field in fields_list:
            print("appending!")
            indices.append(self.current_data_fields.index(field))
        return indices

    def append_product(self, indices, values):
        for index, value in zip(indices, values):
            self.add_data(self.current_row, index, value)
        self.current_row += 1

    def set_file_name(self, output_file_format, output_dir):
        time_string = time.strftime(r"_%A_%d-%m-%Y-%H_%M")
        self.current_filename = fr"{output_dir}\{output_file_format}{time_string}{self.extension}"