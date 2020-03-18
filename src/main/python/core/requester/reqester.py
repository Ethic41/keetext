#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-18 01:51:48
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

from core.requester.get_user_agent import get_user_agent
import requests

# TODO: we should implement get user-agents from internet
# with in this module
class Requester:
    def __init__(self):
        self.user_agent = get_user_agent()
        self.headers = {"user-agent": self.user_agent}
        with requests.Session() as conn:
            self.conn = conn
    
    def make_request(self, url: str, request_method="get", payload: dict=None):
        if request_method == "get":
            request = self.conn.get(url, params=payload, headers=self.headers)
            return request.content
        
        if request_method == "post":
            request = self.conn.post(url, data=payload, headers=self.headers)
            return request.status_code