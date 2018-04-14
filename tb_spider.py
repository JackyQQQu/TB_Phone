# !/usr/bin/env python
# -*- coding:utf-8 -*-
# author:Qu time:2018/3/26

import urllib.error
import urllib.request
import re
import pymysql
import time
import random
from fake_useragent import UserAgent
import http.cookiejar


keyword = "手机"

# 浏览器头
ua = UserAgent()
headers = {
    'User-Agent': ua.random,
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
}
cookie = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)


# 代理IP获取
def proxy_get():
    ip_list = None
    order = "1656e0992966b89d56c14ccff0c88392"
    api_url = "http://dynamic.goubanjia.com/dynamic/get/" + order + ".html?sep=3"
    proxy = urllib.request.ProxyHandler({"http": ""})
    opr = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opr)
    try:
        ip_list = urllib.request.urlopen(api_url, timeout=30).read().decode("utf-8").strip("\n")
        time.sleep(1)
    except Exception as e:
        print("获取失败" + str(e))
    return ip_list


# 使用代理ip访问
def use_proxy(url, proxy_ip):
    proxy = urllib.request.ProxyHandler({"http": proxy_ip})
    opr = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opr)
    data = urllib.request.urlopen(url, timeout=30).read()
    return data


def search(kw, t):
    # 搜索页信息获取
    kw = urllib.request.quote(kw)
    headers['referer'] = 'https://www.taobao.com/'
    opener.addheaders = [headers]
    url1 = "http://s.taobao.com/search?spm=a217h.9580640.831227.16.66ed25aai2uXur&q="+kw+"&p4ppushleft=5%2C48&s="+str(t)
    rst_link, rst_num = None, None
    error = 0
    dt = None
    print("----获取动态IP中----")
    ip = proxy_get()
    print(ip)
    try:
        dt = use_proxy(url1, ip)
    except urllib.error.URLError as e:
        error = 1
        if hasattr(e, "code"):
            print("失败，", e.code)
        if hasattr(e, "reason"):
            print("失败，", e.reason)
        time.sleep(10)  # 延迟10秒
    except Exception as e:
        error = 1
        print("失败，Exception:" + str(e))
        time.sleep(1)  # 延迟1秒
    if dt is not None:
        error = 0
        dt_1 = dt.decode("utf-8")
        dt_2 = dt.decode("unicode_escape")
        pat_link = '"url":"//(s.taobao.com/search?\S*?grid)#'
        pat_num = '"num":"(.*?)"'  # 在售商家数
        rst_link = re.findall(pat_link, dt_2)
        rst_num = re.findall(pat_num, dt_1)
        print("----本页获取成功----")
    else:
        print("----本页获取失败----")
    n = random.random() * 8
    time.sleep(1 + n)
    return url1, error, rst_link, rst_num


def details(r_link, url_refer):
    # 详情页信息获取
    rst_brand, rst_model, rst_ram, rst_size, rst_pixel, \
        rst_core_num, rst_price, rst_month_sales, rst_tag = ["未获取"]*48, ["未获取"]*48, ["未获取"]*48, ["未获取"]*48, \
                                                            ["未获取"]*48, ["未获取"]*48, ["0"]*48, \
                                                            ["0"]*48, ["0"]*48
    i = 1
    for url2 in r_link:
        print("------正在获取第" + str(i) + "个商品------")
        headers['referer'] = url_refer
        opener.addheaders = [headers]
        url2_1 = "http://" + str(url2)
        dt2 = None
        print("----获取动态IP中----")
        ip = proxy_get()
        print(ip)
        try:
            dt2 = use_proxy(url2_1, ip).decode("utf-8")
        except urllib.error.URLError as e:
            if hasattr(e, "code"):
                print("失败，", e.code)
            if hasattr(e, "reason"):
                print("失败，", e.reason)
                time.sleep(10)  # 延迟10秒
        except Exception as e:
            print("失败：" + str(e))
            time.sleep(1)  # 延迟1秒
        if dt2 is not None:
            try:
                print("----正在保存商品信息----")
                pat_brand = '{"name":"品牌","value":"(.*?)"}'
                pat_model = '{"name":"型号","value":"(.*?)"}'
                pat_ram = '{"name":"运行内存RAM","value":"(.*?)"}'
                pat_size = '{"name":"尺寸","value":"(.*?)"}'
                pat_pixel = '{"name":"像素","value":"(.*?)"}'
                pat_core_num = '{"name":"核心数","value":"(.*?)"}'
                pat_price = '"commonPrice":"(.*?)"'  # 价格
                pat_month_sales = '"month_sales":"(.*?)"'  # 月销量
                pat_tag = '{"text":"(.*?)"'  # 特点
                rst_price[i-1] = re.findall(pat_price, dt2)[0]
                rst_month_sales[i-1] = re.findall(pat_month_sales, dt2)[0]
                rst_brand[i-1] = re.findall(pat_brand, dt2)[0]
                rst_model[i-1] = re.findall(pat_model, dt2)[0]
                rst_ram[i-1] = re.findall(pat_ram, dt2)[0]
                rst_size[i-1] = re.findall(pat_size, dt2)[0]
                rst_pixel[i-1] = re.findall(pat_pixel, dt2)[0]
                rst_core_num[i-1] = re.findall(pat_core_num, dt2)[0]
                rst_tag[i-1] = ",".join(re.findall(pat_tag, dt2))
                print("----保存成功----")
                print("该商品为：" + str(rst_brand[i-1]) + str(rst_model[i-1]))
            except Exception as e:
                print(e)
        else:
            print("----此商品获取失败----")
        n = random.random() * 8
        time.sleep(1 + n)
        i += 1
    return rst_brand, rst_model, rst_ram, rst_size, rst_pixel, rst_core_num, rst_price, rst_month_sales, rst_tag


# 执行
brand, model, ram, size, pixel, core_num, price, month_sales = None, None, None, None, None, None, None, None
conn = pymysql.connect("localhost", "root", "7758258", "taobao", use_unicode=True, charset="utf8")
fa = []
for y in range(0, 74):
    print("------正在抓取"+str(y+1)+"页数据------")
    t = y * 44
    url_rf, error_inf, link, num = search(keyword, t)
    if error_inf == 0:
        brand, model, ram, size, pixel, core_num, price, month_sales, tag = details(link, url_rf)
        # 写入数据库
        print("----将本页写入数据库----")
        for i in range(0, len(link)):
            link_data, price_data, tag_data = link[i], price[i], tag[i]
            month_sales_data, num_data = month_sales[i], num[i]
            brand_data, model_data, ram_data = brand[i], model[i], ram[i]
            size_data, pixel_data, core_num_data = size[i], pixel[i], core_num[i]
            sql = "insert into data(link, price, month_sales, num, brand, model, ram, size, pixel, core_num, tag) " \
                  "values('" + link_data + "','" + price_data + "','" + month_sales_data + "','" + num_data + "'," \
                  "'" + brand_data + "','" + model_data + "','" + ram_data + "','" + size_data + "','" + pixel_data + "'," \
                  "'" + core_num_data + "','" + tag_data + "')"
            conn.query(sql)
            conn.commit()
        print("----写入完成----")
    else:
        print("本页获取失败")
        fa.append(str(y+1))  # 记录失败页
conn.close()
print(fa)
