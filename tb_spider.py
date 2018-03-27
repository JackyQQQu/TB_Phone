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
    if __name__ == '__main__':
        order = "1656e0992966b89d56c14ccff0c88392"
        api_url = "http://dynamic.goubanjia.com/dynamic/get/" + order + ".html?sep=3"
        ip = None
        try:
            ip = urllib.request.urlopen(api_url).read()
        except Exception as e:
            print(e)
        return ip


# 使用代理ip访问
def use_proxy(url, proxy_ip):
    proxy = urllib.request.ProxyHandler({"http": proxy_ip})
    opr = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opr)
    data = urllib.request.urlopen(url).read()
    return data


def search(kw, t):
    # 搜索页信息获取
    kw = urllib.request.quote(kw)
    headers['referer'] = 'https://www.taobao.com/'
    opener.addheaders = [headers]
    url1 = "http://s.taobao.com/search?spm=a217h.9580640.831227.16.66ed25aai2uXur&q="+kw+"&p4ppushleft=5%2C48&s="+str(t)
    ip = proxy_get().decode("utf-8")
    dt = None
    try:
        dt = use_proxy(url1, ip)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print("失败，", e.code)
        if hasattr(e, "reason"):
            print("失败，", e.reason)
            time.sleep(10)  # 延迟10秒
    except Exception as e:
        print("失败，Exception:" + str(e))
        time.sleep(1)  # 延迟1秒
    n = random.random() * 8
    time.sleep(1 + n)
    dt_1 = dt.decode("utf-8")
    dt_2 = dt.decode("unicode_escape")
    pat_link = '"url":"//(s.taobao.com/search?\S*?grid)#'
    pat_price = '"price":"(.*?)"'  # 价格
    pat_month_sales = '"month_sales":"(.*?)"'  # 月销量
    pat_num = '"num":"(.*?)"'  # 在售商家数
    rst_link = re.findall(pat_link, dt_2)
    rst_price = re.findall(pat_price, dt_1)
    rst_month_sales = re.findall(pat_month_sales, dt_1)
    rst_num = re.findall(pat_num, dt_1)
    return rst_link, rst_price, rst_month_sales, rst_num, url1


def details(r_link, url_refer):
    # 详情页信息获取
    rst_brand, rst_model, rst_ram, rst_size, rst_pixel, rst_core_num = None, None, None, None, None, None
    i = 1
    for url2 in r_link:
        print("------正在获取第" + str(i) + "个商品------")
        headers['referer'] = url_refer
        opener.addheaders = [headers]
        url2_1 = "http://" + str(url2)
        ip = proxy_get().decode("utf-8")
        try:
            dt2 = use_proxy(url2_1, ip).decode("utf-8")
        except urllib.error.URLError as e:
            if hasattr(e, "code"):
                print("失败，", e.code)
            if hasattr(e, "reason"):
                print("失败，", e.reason)
                time.sleep(10)  # 延迟10秒
        except Exception as e:
            print("失败，Exception:" + str(e))
            time.sleep(1)  # 延迟1秒
        n = random.random() * 6
        time.sleep(1 + n)
        pat_brand = '{"name":"品牌","value":"(.*?)"}'
        pat_model = '{"name":"型号","value":"(.*?)"}'
        pat_ram = '{"name":"运行内存RAM","value":"(.*?)"}'
        pat_size = '{"name":"尺寸","value":"(.*?)"}'
        pat_pixel = '{"name":"像素","value":"(.*?)"}'
        pat_core_num = '{"name":"核心数","value":"(.*?)"}'
        rst_brand = re.findall(pat_brand, dt2)
        rst_model = re.findall(pat_model, dt2)
        rst_ram = re.findall(pat_ram, dt2)
        rst_size = re.findall(pat_size, dt2)
        rst_pixel = re.findall(pat_pixel, dt2)
        rst_core_num = re.findall(pat_core_num, dt2)
        i += 1
    return rst_brand, rst_model, rst_ram, rst_size, rst_pixel, rst_core_num


# 执行
# for t in range(0, 99):
        # print("------正在抓取"+str(t+1)+"页数据------")
        # t = t * 44
link, price, month_sales, num, url_rf = search(keyword, t=0)
brand, model, ram, size, pixel, core_num = details(link, url_rf)
# 写入数据库
conn = pymysql.connect("localhost", "root", "7758258", "taobao", use_unicode=True, charset="utf8")
for i in range(0, len(link)):
    link_data, price_data = link[i], price[i]
    month_sales_data, num_data = month_sales[i], num[i]
    brand_data, model_data, ram_data = brand[i], model[i], ram[i]
    size_data, pixel_data, core_num_data = size[i], pixel[i], core_num[i]
    sql = "insert into data(link, price, month_sales, num, brand, model, ram, size, pixel, core_num) " \
          "values('" + link_data + "','" + price_data + "','" + month_sales_data + "','" + num_data + "'," \
          "'" + brand_data + "','" + model_data + "','" + ram_data + "','" + size_data + "','" + pixel_data + "'," \
          "'" + core_num_data + "')"
    conn.query(sql)
    conn.commit()
conn.close()
