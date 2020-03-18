#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-18 02:30:24
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)

import requests

user_agent_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

def get_user_agent()->str:
    # TODO: implement getting user-agent-string from
    # internet here
    return user_agent_string


if __name__ == "__main__":
    get_user_agent()