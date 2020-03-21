#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-19 13:09:17
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

from ui.main_window import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os


class KeetextGui(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(KeetextGui, self).__init__()
        self.setupUi(self)
        