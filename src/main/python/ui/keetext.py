#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-19 13:09:17
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

from core.amazon_scraper.scraper import Scraper
from ui.main_window import Ui_MainWindow
import ui.base_rc
from PyQt5 import QtCore, QtGui, QtWidgets
from core.amazon_scraper.structures import ListWidgetItem, Category
from threading import Thread
import threading
from time import sleep
import os


class KeetextGui(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super(KeetextGui, self).__init__()

        # instantiate the scraper class
        self.scraper = Scraper()

        # user data implementation for QListWidgetItem
        self.user_data = 0x0100
        self.available = "available"
        self.not_available = "not available"
        self.selected_rating = 3
        self.selected_product_status = self.not_available
        self.output_dir = os.getcwd()
        self.all_in_one_format = "all"
        self.category_format = "category"
        self.subcategory_format = "subcategory"

        self.workers_1 = []
        self.workers_2 = []
        self.workers_3 = []
        self.workers_4 = []
        self.finder_thread: Thread = None

        self.output_format = self.all_in_one_format

        # set up the initial user interface
        self.setupUi(self)

        # set categories and subcategories
        self.scraper.set_categories_and_subcategories()
        
        # set up all icons
        self.category_icon = QtGui.QIcon()
        self.category_icon.addPixmap(QtGui.QPixmap(":/base/grid.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.subcategory_icon = QtGui.QIcon()
        self.subcategory_icon.addPixmap(QtGui.QPixmap(":/base/backend.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.excel_icon = QtGui.QIcon()
        self.excel_icon.addPixmap(QtGui.QPixmap(":/base/excel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        # connect button clicked
        self.connectButton.clicked.connect(self.start)

        self.selectCategoryListWidget.clicked.connect(self.display_subcategories)

        self.selectSubcategoryListWidget.clicked.connect(self.select_subcategory)

        # url chosen
        self.urlComboBox.currentIndexChanged.connect(self.change_base_url)

        # category check all clicked
        self.selectAllCategoriesCheckBox.stateChanged.connect(self.all_category_clicked)

        # subcategory check all clicked
        self.selectAllSubcategoryCheckBox.clicked.connect(self.all_subcategory_clicked)

        # clear selectCategoryListWidget
        self.clear_list_widget_items(self.selectCategoryListWidget)

        # clear selectSubcategoryListWidget
        self.clear_list_widget_items(self.selectSubcategoryListWidget)

        # output directory list clear
        self.clear_list_widget_items(self.outputDirectoryListWidget)

        # display categories
        self.display_categories()

        # refresh button clicked to retrieve new categories
        self.categoryRefreshButton.clicked.connect(self.refresh)

        # connecting radio buttons
        self.oneStarRadioButton.clicked.connect(self.set_star_rating)
        self.twoStarRadioButton.clicked.connect(self.set_star_rating)
        self.threeStarRadioButton.clicked.connect(self.set_star_rating)
        self.fourStarRadioButton.clicked.connect(self.set_star_rating)

        self.availableProductRadioButton.clicked.connect(self.set_product_status)
        self.notAvailableProductRadioButton.clicked.connect(self.set_product_status)

        self.outputComboBox.currentIndexChanged.connect(self.set_output_format)

        self.outputDirectoryBrowseButton.clicked.connect(self.choose_output_dir)

        self.outputDirectoryLineEdit.textChanged.connect(self.show_output_dir_files)
        self.outputDirectoryListWidget.clicked.connect(self.show_output_dir_files)
        
        # search button clicked
        self.searchPushButton.clicked.connect(self.start_search)

        status_thread = Thread(target=self.status_tracking)
        status_thread.start()

    def show_output_dir_files(self):
        try:
            # clear any existing item b4 we populate the list
            self.clear_list_widget_items(self.outputDirectoryListWidget)

            # Get the user specified directory and extract the files
            output_dir = self.outputDirectoryLineEdit.text()
            if output_dir:
                self.output_dir = output_dir
            dir_items = os.listdir(self.output_dir)
            for item in dir_items:
                full_path = fr"{output_dir}/{item}"
                if os.path.isfile(full_path):
                    if item.endswith("xlsx") or item.endswith("xls") or item.endswith("csv"):
                        output_file = QtWidgets.QListWidgetItem()
                        output_file.setIcon(self.excel_icon)
                        output_file.setCheckState(QtCore.Qt.Unchecked)
                        output_file.setText(item)
                        self.outputDirectoryListWidget.addItem(output_file)
        except Exception as e:
            print(e)
    
    def choose_output_dir(self):
        try:
            output_dialog = QtWidgets.QFileDialog(self)
            output_dialog.setWindowTitle("Select Output Directory")
            output_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
            output_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
            output_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
            output_dialog.open()
            if output_dialog.exec():
                self.outputDirectoryLineEdit.setText(output_dialog.selectedFiles()[0])
        except Exception as e:
            print(e)

    def set_output_format(self):
        if self.outputComboBox.currentIndex() == 0:
            self.output_format = self.all_in_one_format
        elif self.outputComboBox.currentIndex() == 1:
            self.output_format = self.category_format
        elif self.outputComboBox.currentIndex() == 2:
            self.output_format = self.subcategory_format
    
    def set_product_status(self):
        if self.availableProductRadioButton.isChecked():
            self.selected_product_status = self.available
        
        if self.notAvailableProductRadioButton.isChecked():
            self.selected_product_status = self.not_available

    def set_star_rating(self):
        if self.oneStarRadioButton.isChecked():
            self.selected_rating = 1
        
        elif self.twoStarRadioButton.isChecked():
            self.selected_rating = 2
        
        elif self.threeStarRadioButton.isChecked():
            self.selected_rating = 3
        
        elif self.fourStarRadioButton.isChecked():
            self.selected_rating = 4

    def display_categories(self):
        category_widget = self.selectCategoryListWidget

        for category in self.scraper.categories:
            category_widget_item = QtWidgets.QListWidgetItem()
            category_widget_item.setIcon(self.category_icon)
            category_widget_item.setCheckState(QtCore.Qt.Unchecked)
            category_widget_item.setData(self.user_data, category)
            category_widget_item.setText(category.category_name)
            category_widget.addItem(category_widget_item)
    
    def display_subcategories(self):
        subcategory_widget = self.selectSubcategoryListWidget
        category_widget = self.selectCategoryListWidget
        category_widget_items_count = category_widget.count()
        

        for item_num in range(category_widget_items_count):
            current_category_item: ListWidgetItem = category_widget.item(item_num)
            current_item_data: Category = current_category_item.data(self.user_data)
            
            if (current_category_item.checkState() == QtCore.Qt.Checked) and not current_item_data.subcat_displayed:
                # if item is checked and subcat data has not yet been displayed
                for subcategory in self.scraper.subcategories:
                    if subcategory.category_id == current_item_data.category_id:
                        subcategory_widget_item = QtWidgets.QListWidgetItem()
                        subcategory_widget_item.setIcon(self.subcategory_icon)
                        subcategory_widget_item.setCheckState(QtCore.Qt.Unchecked)
                        subcategory_widget_item.setData(self.user_data, subcategory)
                        subcategory_widget_item.setText(subcategory.name)
                        subcategory_widget.addItem(subcategory_widget_item)
                current_item_data.selected = True
                current_item_data.subcat_displayed = True
            
            elif (current_category_item.checkState() == QtCore.Qt.Unchecked) and current_item_data.subcat_displayed:
                # if item is unchecked but subcategory data displayed we need to remove it
                removed_count = 0
                subcategory_widget_item_count = subcategory_widget.count()
                for subcat_item_num in range(subcategory_widget_item_count):
                    current_subcat_item: ListWidgetItem = subcategory_widget.item(subcat_item_num - removed_count)
                    current_subcat_item_data: Category = current_subcat_item.data(self.user_data)

                    if current_item_data.category_id == current_subcat_item_data.category_id:
                        # if belong to unchecked category, then we need to remove
                        current_item_data.selected = False
                        current_item_data.subcat_displayed = False
                        current_subcat_item_data.selected = False
                        subcategory_widget.takeItem(subcat_item_num - removed_count)
                        removed_count += 1

    def select_subcategory(self):
        subcategory_widget = self.selectSubcategoryListWidget
        subcategory_widget_item_count = subcategory_widget.count()

        for item_num in range(subcategory_widget_item_count):
            current_subcategory_item: ListWidgetItem = subcategory_widget.item(item_num)
            current_item_data: Category = current_subcategory_item.data(self.user_data)

            if current_subcategory_item.checkState() == QtCore.Qt.Checked:
                current_item_data.selected = True
            elif current_subcategory_item.checkState() == QtCore.Qt.Unchecked:
                current_item_data.selected = False

    def clear_list_widget_items(self, widget_name):
        try:
            widget = widget_name
            item_count = widget.count()

            for _ in range(item_count):
                item = widget.takeItem(0)
                del item  # manually deleting because Qt won't help us here
        except Exception as e:
            print(e)
    
    def start_scraping(self):
        main_thread = threading.main_thread()
        min_rank = self.minimumRankSpinBox.value()
        max_rank = self.maximumRankSpinBox.value()
        min_subrank = self.minimumSubrankSpinBox.value()
        max_subrank = self.maximumSubrankSpinBox.value()
        self.scraper.started = True
        self.scraper.stopped = False
        self.scraper.filter_by_rating(self.selected_rating)
        self.scraper.filter_by_include_not_available()
        self.scraper.retrieve_not_available_item(self.output_format, self.output_dir, min_rank=min_rank, max_rank=max_rank, min_subrank=min_subrank, max_subrank=max_subrank)
        if not main_thread.is_alive():
            exit(0)
        
        if self.scraper.stopped == True:
            exit(0)
            
        self.show_output_dir_files()
    
    def stop_scraping(self):
        self.scraper.started = False
        self.scraper.stopped = True
        self.scraper.scrape_status = self.scraper.stopping_status
    
    def stop_searching(self):
        self.scraper.started_search = False
        self.scraper.stopped_search = True
        self.scraper.scrape_status = self.scraper.searching_stopped_status
    
    def start(self):
        if self.connectButton.text() == "Start":
            self.connectButton.setText("Stop")
            scraper_thread = Thread(target=self.start_scraping)
            scraper_thread.start()
            
        elif self.connectButton.text() == "Stop":
            self.connectButton.setText("Start")
            self.stop_scraping()
    
    def start_search(self):
        self.scraper.started_search = True
        self.scraper.stopped_search = False
        
        min_rank = self.minimumRankSpinBox.value()
        max_rank = self.maximumRankSpinBox.value()
        min_subrank = self.minimumSubrankSpinBox.value()
        max_subrank = self.maximumSubrankSpinBox.value()

        if self.searchPushButton.text() == "Search":
            self.searchPushButton.setText("Stop")

            # start finder thread
            self.finder_thread = Thread(target=self.scraper.search, args=(self.searchComboBox.currentText(), ))
            self.finder_thread.start()

            
            # start workers_1 threads rating_filters
            workers_1_count = 1
            self.workers_1 = []
            for _ in range(workers_1_count):
                worker = Thread(target=self.scraper.apply_rating_filter_to_search, args=(self.selected_rating, self.finder_thread))
                self.workers_1.append(worker)
            
            for worker in self.workers_1:
                worker.start()
            
            
            # start workers_2 threads not_available_filters
            workers_2_count = 1
            self.workers_2 = []
            for _ in range(workers_2_count):
                worker = Thread(target=self.scraper.apply_include_not_available_filter_to_search, args=(self.workers_1, ))
                self.workers_2.append(worker)
            
            for worker in self.workers_2:
                worker.start()
            
            
            # start worker_3 thread product url retrievers
            workers_3_count = 1
            self.workers_3 = []
            for _ in range(workers_3_count):
                worker = Thread(target=self.scraper.retrieve_product_url, args=(self.workers_2, ))
                self.workers_3.append(worker)
            
            for worker in self.workers_3:
                worker.start()
            
            
            # start worker_4 thread product retrievers
            workers_4_count = 1
            self.workers_4 = []
            for _ in range(workers_4_count):
                worker = Thread(target=self.scraper.retrieve_product, args=((self.workers_3), min_rank, max_rank, min_subrank, max_subrank))
                self.workers_4.append(worker)
            
            for worker in self.workers_4:
                worker.start()
            
            writer_thread = Thread(target=self.scraper.write_retrieved_product, args=(self.output_format, self.output_dir, (self.workers_4)))
            writer_thread.start() 
            
        elif self.searchPushButton.text() == "Stop":
            self.searchPushButton.setText("Search")
            self.stop_searching()
    
    def status_tracking(self):
        main_thread = threading.main_thread()
        while main_thread.is_alive():
            self.programStatus.setText(self.scraper.scrape_status)
            sleep(1)
        exit(0)

    def change_base_url(self):
        self.scraper.base_url = self.urlComboBox.currentText()

    def all_category_clicked(self):
        if self.selectAllCategoriesCheckBox.checkState() == QtCore.Qt.Checked:
            self.check_all(self.selectCategoryListWidget)
        
        else:
            self.uncheck_all(self.selectCategoryListWidget)
        
        self.display_subcategories()

    def all_subcategory_clicked(self):
        if self.selectAllSubcategoryCheckBox.checkState() == QtCore.Qt.Checked:
            self.check_all(self.selectSubcategoryListWidget)
        
        else:
            self.uncheck_all(self.selectSubcategoryListWidget)
        
        self.select_subcategory()
        
    def check_all(self, widget_name):
        try:
            widget = widget_name
            item_count = widget.count()

            for item_num in range(item_count):
                widget_item = widget.item(item_num)
                widget_item.setCheckState(QtCore.Qt.Checked)
        except Exception as e:
            print(e)

    def uncheck_all(self, widget_name):
        try:
            widget = widget_name
            item_count = widget.count()

            for item_num in range(item_count):
                widget_item = widget.item(item_num)
                widget_item.setCheckState(QtCore.Qt.Unchecked)
        except Exception as e:
            print(e)

    def refresh(self):
        refresh_thread = Thread(target=self.refresh_categories)
        refresh_thread.start()
    
    def refresh_categories(self):
        self.scraper.set_categories_and_subcategories()   # retrieve new categories and subcategories
        self.clear_list_widget_items(self.selectCategoryListWidget)
        self.display_categories()
        self.clear_list_widget_items(self.selectSubcategoryListWidget)
        exit(0)