#! /usr/local/bin/python3
# -*- coding: UTF-8 -*-
# 京东登录界面

import tkinter as tk
from tkinter import *
from selenium import webdriver
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
# def get_user_name():
#     user_name.set()


wd = webdriver.Firefox()  # webdriver.Firefox() webdriver.PhantomJS('')

url = 'https://try.jd.com/400370.html'
try:
    wd.get(url)
    wait = WebDriverWait(wd, timeout=10)

    sleep(2)
    # 查找 '申请试用' 并点击
    element = wd.find_element_by_xpath("//div[contains(@class, 'info')]")
    elem = element.find_element_by_xpath("//div[contains(@class, 'btn-wrap')]/a")
    elem.click()
    print('elem.text:', elem.text)
    # for handle in wd.window_handles:  # 始终获得当前最后的窗口
    #     wd.switch_to.window(handle)

    # # print('element:', element, 'element.text', element[0].text)
    # for ele in element:
    #     e = ele.find_element_by_xpath("//div[contains(@class, 'btn-wrap')]/a")
    #     print('e:', e, '\ne.text:', e.text)
    #     if e.text == '申请试用':
    #         # ActionChains(wd).move_to_element(e).perform()
    #         e.click()
    #         break
    #     else:
    #         print("不是")
    #         continue

    # element2 = element.find_element_by_xpath("//div[contains(@class, 'info-detail .chosen')]")
    # print('element2:', element2)
except NoSuchElementException as e:
    print("异常信息：", e.msg)


# root = tk.Tk()
# user_name = StringVar()  # 用户名
# user_password = StringVar()  # 密码
#
# # 用户名
# label_user_name = tk.Label(root, text='用户名：').grid(row=0, column=0)
# tk.Entry(root, textvariable=user_name).grid(row=0, column=1)
# # 密码
# label_user_password = tk.Label(root, text='密码：').grid(row=1, column=0)
# tk.Entry(root, textvariable=user_password).grid(row=1, column=1)
