#! /usr/local/bin/python3
# -*- coding: UTF-8 -*-
#

import cv2
from time import sleep
import numpy as np
from urllib import request, parse
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import threading  # 多线程

options = Options()
options.add_argument('-headless')  # 无头参数
options.add_argument('--disable-gpu')
wd = webdriver.Firefox()  # webdriver.Firefox() webdriver.PhantomJS('')
# 当前窗口
current_window = wd.current_window_handle
# 当前程序锁
lock = threading.Lock()
# 当前点击
current_index = -1  # -1
# 当前页数
current_page = 0


# 显示图片，查看二值后的滑块和背景图片
def show(template, x, y, w, h, block):
    # 展示圈出来的区域
    cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
    cv2.imshow('template', template)
    cv2.imshow('block', block)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 获取图形验证的图片，并滑动滑块实现滑块验证处理
def get_image_position():
    # 获取滑块图片的下载地址
    image1 = wd.find_element_by_class_name('JDJRV-smallimg').find_element_by_xpath('img').get_attribute('src')
    # 获取背景大图图片的下载地址
    image2 = wd.find_element_by_class_name('JDJRV-bigimg').find_element_by_xpath('img').get_attribute('src')
    # print("image1:", image1)
    # print("image2:", image2)
    if image1 is None or image2 is None:
        return

    if wd.find_element_by_class_name('JDJRV-smallimg').is_displayed() is False:
        return

    image1_name = 'slide_block.png'  # 滑块图片名
    image2_name = 'slide_bkg.png'   # 背景大图名

    # 下载滑块图片并存储到本地
    request.urlretrieve(image1, image1_name)
    # 下载背景大图并存储到本地
    request.urlretrieve(image2, image2_name)

    # 获取图片，并灰化
    block = cv2.imread(image1_name, 0)
    template = cv2.imread(image2_name, 0)

    # 二值化之后的图片名称
    block_name = 'block.jpg'
    template_name = 'template.jpg'
    # 将二值化后的图片进行保存
    cv2.imwrite(template_name, template)
    cv2.imwrite(block_name, block)
    block = cv2.imread(block_name)
    block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    block = abs(255 - block)
    cv2.imwrite(block_name, block)

    block = cv2.imread(block_name)
    template = cv2.imread(template_name)

    # 获取偏移量
    result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED)  # 查找block图片在template中的匹配位置，result是一个矩阵，返回每个点的匹配结果
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # print("min_val", min_val, "max_val", max_val, "min_loc", min_loc, "max_loc", max_loc)

    x, y = np.unravel_index(result.argmax(), result.shape)
    # print("x,y:", x, y, 'result.shape:', result.shape)

    # # # 显示图片
    # w, h = block.shape[::-1]
    # print('\nw:', w, ' h:', h)
    # show(template, x, y, w, h, block)
    # show(template, min_val, max_val, min_loc, max_loc, block)

    # 获取滑块
    element = wd.find_element_by_class_name('JDJRV-slide-inner.JDJRV-slide-btn')
    # 滑动滑块
    ActionChains(wd).click_and_hold(on_element=element).perform()
    # print("x方向的偏移", int(y * 0.4 + 18), 'x:', x, 'y:', y)
    ActionChains(wd).move_to_element_with_offset(to_element=element, xoffset=y, yoffset=0).perform()
    # sleep(1)
    ActionChains(wd).release(on_element=element).perform()
    sleep(3)


# 打开浏览器
def open_firefox(user_name, user_password, page):
    # url = 'https://try.jd.com/'
    global current_page
    url = 'https://try.jd.com/activity/getActivityList'  # 全部试用 https://try.jd.com/activity/getActivityList?page=2
    try:
        page_num = '?page=%s' % page
        current_page = int(page)
        wd.get(url+page_num)
        wait = WebDriverWait(wd, timeout=13)
        # # wait.until(expected_conditions.title_is("京东试用-专业的综合网上免费试用平台"))
        # # wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, '.link-login')))

        # 登录和验证
        res = login_validation(user_name, user_password)

        if res is False:
            return

        again_to_applicable()

        # for num1 in array1:
        #     # 锁定申请流程
        #     lock.acquire()
        #     current_index = current_index + 1
        #     print("执行了一次")
        #     apply_for_good(num1)
        #     lock.release()

    except NoSuchElementException as e:
        print("异常信息：", e.msg)


# 关闭当前页面也没法切换回上一个window
def again_to_applicable():
    global current_index
    global current_page
    if current_index < 19:
        current_index = current_index + 1
        applicable_operation()
    else:
        current_index = 0
        wd.switch_to.window(wd.window_handles[0])  # 页面进行了刷新，重新进行句柄的获取
        # 换到第二页
        # if is_element_exist("//span[contains(@id, 'pager')]/a[contains(@class, 'ui-pager-next')]", False):
        if is_element_exist('ui-pager-next', True):
            elem = wd.find_element_by_class_name('ui-pager-next')
            # elem = wd.find_element_by_xpath("//span[contains(@id, 'pager')]/a[contains(@class, 'ui-pager-next')]")
            elem.click()
            # page = elem.get_attribute('rel')
            current_page = current_page + 1
            print("\n 点击了下一页 ------ 当前页数:", current_page, '\n')
            # print("当前是第%s页" % page)

            applicable_operation()
        else:
            print("未找到页数按钮")


# 修改页面之后再进行当前操作
def applicable_operation():
    print("=============current_index: ", current_index)
    sleep(2)

    # print("当前窗口：", wd.window_handles[0])

    wd.switch_to.window(wd.window_handles[0])  # 切换到列表页

    array = wd.find_element_by_class_name('con')
    array1 = array.find_elements_by_class_name('item')  # 获取所有的商品列表
    print("开始查找")
    # 锁定申请流程
    # lock.acquire()
    # print("执行了一次")
    apply_for_good(array1[current_index])
    # lock.release()


# 申请的整个流程
def apply_for_good(good):

    good.find_element_by_class_name('link').click()   # 我要申请

    sleep(1)
    # if current_window != wd.window_handles[0]:
    change_current_window()

    sleep(2)
    print("开始申请流程")
    # 查找 '申请试用' 并点击
    if is_element_exist("//div[contains(@class, 'info')]", False) and wd.find_element_by_xpath("//div[contains(@class, 'state')]").text == '活动已开始，请快快申请吧！':
        element = wd.find_element_by_xpath("//div[contains(@class, 'info')]")
        if is_element_exist("//div[contains(@class, 'btn-wrap')]/a", False):  # 申请试用
            elem = element.find_element_by_xpath("//div[contains(@class, 'btn-wrap')]/a")
            elem.click()  # 申请试用
            print("申请试用")
            sleep(2)

            # 关注店铺才能申请 ui-dialog整个弹窗
            if is_element_exist('tip-tit', True) == False and is_element_exist('ui-dialog-content', True) and wd.find_element_by_class_name('ui-dialog-content').find_element_by_class_name('y').is_displayed():
                sleep(3)
                print("关注并申请")
                wd.find_element_by_class_name('ui-dialog-content').find_element_by_class_name('y').click()
                # wd.find_element_by_xpath("//div[contains(@class, 'btn')]/a[contains(@class, 'y')]").is_displayed():

                # is_element_exist("//div[contains(@class, 'btn')]/a[contains(@class, 'y')]", False):

                # wd.find_element_by_xpath("//div[contains(@class, 'btn')]/a[contains(@class, 'y')]").text == '关注并申请'
                # wd.find_element_by_xpath("//div[contains(@class, 'btn')]/a[contains(@class, 'y')]").click()

                sleep(1.5)

                # 如果出现申请成功的弹窗，关闭当前页面，切换window
                if is_element_exist('tip-tit', True) and wd.find_element_by_class_name('tip-tit').is_displayed():
                    # wd.find_element_by_class_name('ui-dialog-close').click()  # 申请成功
                    print("已成功申请")

                else:
                    print("未成功申请")
                sleep(1)
                wd.close()
                again_to_applicable()
            # tip-tit 申请成功文字 apply-tip apply-tip1 申请成功内容弹窗
            elif is_element_exist('tip-tit', True) and wd.find_element_by_class_name('tip-tit').is_displayed():
                # 不需关注店铺，直接申请，且成功
                print("已成功申请")
                sleep(1)
                wd.close()
                again_to_applicable()
            elif is_element_exist('link-login', True) and wd.find_element_by_class_name('link-login').is_displayed():   # 出现登录弹窗
                print("出现登录")   # 暂时未处理，调用登录方法即可
                wd.close()
                sleep(1)
                again_to_applicable()
            else:
                print("未找到关注并申请")
                wd.close()
                # for window in wd.window_handles:
                #     if window != wd.window_handles[0]:
                #         wd.window_handles
                sleep(1)
                again_to_applicable()

        elif is_element_exist("//div[contains(@class, 'state')]", False) and wd.find_element_by_xpath("//div[contains(@class, 'state')]").text == '您已提交申请，等待系统审核…':
            print("已申请，等待审核")
            wd.close()  # 已申请，等待审核
            sleep(1)
            again_to_applicable()
        else:
            print("未找到申请试用")
            wd.close()
            sleep(1)
            again_to_applicable()
    elif is_element_exist('app-btn', True) and wd.find_element_by_class_name('app-btn').text == '查看更多试用':
        # 申请过，当前页面显示查看更过试用
        print("已申请,查看更多试用")
        sleep(1)
        wd.close()
        sleep(1)
        again_to_applicable()
    else:
        print("未找到申请试用")
        wd.close()  # 关闭当前窗口
        sleep(1)
        print("关闭当前窗口")
        again_to_applicable()


# 切换到当前窗口
def change_current_window():
    global current_window
    # print("\n所有窗口:", wd.window_handles, '\n')
    print("前 ----- 当前窗口", current_window)
    # 始终获得当前最后的窗口
    wd.switch_to.window(wd.window_handles[len(wd.window_handles)-1])
    current_window = wd.window_handles[len(wd.window_handles)-1]
    print("后 ----- 当前窗口", current_window)


# 登录和验证
def login_validation(user_name, user_password):
    wd.find_element_by_class_name('link-login').click()
    wd.find_element_by_css_selector(".login-tab.login-tab-r").click()
    # 自动填充用户名
    input_user_name = wd.find_element_by_id('loginname')
    input_user_name.send_keys(user_name)
    # 自动填充密码
    input_user_password = wd.find_element_by_id('nloginpwd')
    input_user_password.send_keys(user_password)
    # 登录
    wd.find_element_by_id('loginsubmit').click()

    # 判断是否需要滑块验证 wd.find_element_by_class_name('JDJRV-smallimg').is_displayed() and
    while is_element_exist('JDJRV-smallimg', True) and wd.find_element_by_class_name('JDJRV-smallimg').is_enabled():
        get_image_position()
    else:
        # 判断账户名和密码输入是否正确
        if is_element_exist('msg-error', True) and wd.find_element_by_class_name('msg-er43ror').is_displayed():
            messagebox.showinfo("温馨提示", "账户名与密码不匹配，请重新输入")
            return False
        else:
            # wd.switch_to.default_content()
            return True


# 判断元素是否存在
def is_element_exist(name, by_class):
    if by_class:
        try:
            wd.find_element_by_class_name(name)
            return True
        except NoSuchElementException:
            return False
    else:
        try:
            wd.find_element_by_xpath(name)
            return True
        except NoSuchElementException:
            return False


if __name__ == '__main__':
    username = input("请输入用户名，点击enter：")
    password = input("请输入密码，点击enter：")
    page_begin = input("请输入开始页码，没有输入0，点击enter：")
    open_firefox(username, password, page_begin)

    # current_url = 'https://try.jd.com/activity/getActivityList'
    # analysis_content(current_url, '1')


# 下载图片暂不可用
# from urllib.request import Request
# ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0'
#
# # 下载滑块图片
# req = urllib.request.Request(image1, headers={'User-Agent': ua})
# f = open(image1_name, 'w')
# f.write(urllib.request.urlopen(req).read())
# print("\n\n1", urllib.request.urlopen(req).read())
# f.close()
#
# # 下载背景大图
# req = urllib.request.Request(image2, headers={'User-Agent': ua})
# f = open(image2_name, 'w')
# f.write(urllib.request.urlopen(req).read())
# print("\n\n2", urllib.request.urlopen(req).read())
# f.close()


# from bs4 import BeautifulSoup
# # 分析数据，生成字典
# def analysis_content(url, page):
#     content = get_current_page_content(url, page)
#     soup = BeautifulSoup(content, 'html.parser')
#     goods_info = soup.find_all('ul', attrs={'clstag': 'secondtype|keycount|try|LBDP'})
#
#     # print("\ngoods_info:", goods_info)
#     # print('\n\nfind_all:\n', soup.find_all('ul', attrs={'clstag': 'secondtype|keycount|try|LBDP'}), '\n\n')
#     result = []
#     for good in goods_info:
#         data = {}
#         good_dict = good.select('li')
#
#
# # 获取当前页面的所有列表数据
# def get_current_page_content(url, page):
#     params = {'page': page}
#     params_parse = parse.urlencode(params)
#     opener = request.urlopen(url+params_parse)
#     content = opener.read()
#     # print('content: \n %s \n' % content)
#     opener.close()
#     return content

# # 切换到当前窗口前一个
# def change_to_last_window():
#     global current_window
#     handles = wd.window_handles
#     wd.switch_to.window(handles[-2])
#     current_window = handles[-2]

