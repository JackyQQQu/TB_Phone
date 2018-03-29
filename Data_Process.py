# coding:utf-8

import numpy as np
import pandas as pda
import matplotlib.pyplot as pp
import collections
from sklearn.cluster import KMeans
import re
import jieba
from wordcloud import WordCloud
from scipy.misc import imread

pp.rcParams['font.sans-serif'] = ['SimHei']   # 用来正常显示中文标签
pp.rcParams['axes.unicode_minus'] = False   # 用来正常显示负号
# 读取数据
data1 = pda.read_excel("E:\\编程学习\\Project\\taobao\\tbphone1.xlsx")
org_num = len(data1)
data2 = data1.T


# 数据清洗
# 缺失值
# 去除获取失败和价格为0的数据
for i in range(0, len(data1)):
    if data2.values[1][i] == "0" or data2.values[1][i] == "未获取" or data2.values[1][i] == "未知":
        data1.drop(i, axis=0, inplace=True)
data2 = data1.T
drop_num = org_num - len(data1)
print("原始数据共" + str(org_num) + "条，删除无效数据" + str(drop_num) + "条，剩余" + str(len(data1)) + "条")

# 异常值
# 查找异常值
price_list = data2.values[1]   # 价格
price_list = np.array(list(map(int, price_list)))
month_sales_list = data2.values[2]  # 月销量
month_sales_list = np.array(list(map(int, month_sales_list)))
# pp.plot(price_list, month_num_list, "o")
# pp.title("价格-销量散点图")
# pp.ylabel("月销量（部）")
# pp.xlabel("价格（元）")

# 去除异常值
data1 = data1.reset_index(drop=True)
for i in range(0, len(data1)):
    if price_list[i] > 9000 or month_sales_list[i] > 80000:
        data1.drop(i, axis=0, inplace=True)
print("去除异常值后，剩余有效信息" + str(len(data1)) + "条")
data = data1.T
price_list = data.values[1]   # 价格
price_list = np.array(list(map(int, price_list)))
month_sales_list = data.values[2]  # 月销量
month_sales_list = np.array(list(map(int, month_sales_list)))
# pp.plot(price_list, month_num_list, "o")

# 数据分布探索
# 极差
price_rg = price_list.max() - price_list.min()
month_sales_rg = month_sales_list.max() - month_sales_list.min()
# 价格分布直方图
bins = np.arange(price_list.min(), price_list.max(), price_rg/18)
# pp.hist(price_list, bins)
# pp.title("价格分布直方图")
# 月销量分布直方图
bins2 = np.arange(month_sales_list.min(), month_sales_list.max(), month_sales_rg/24)
# pp.hist(month_sales_list, bins2, color="y")
# pp.title("月销量分布直方图")

# 统计不同品牌的销量情况和最受欢迎的手机型号
bd_ms = data1.groupby(['brand'])['month_sales'].sum().sort_values(ascending=True)
# bd_ms[-15:].plot(kind="barh", title="品牌销量排行")
md_ms = data1.groupby(['model'])['month_sales'].sum().sort_values(ascending=True)
# md_ms[-15:].plot(kind="barh", title="最受欢迎手机型号排行")

# 统计不同品牌的销量占比
brand_list = data.values[4].tolist()
bd_da = bd_ms[-10:]
bd_da = bd_da.index
ms_data = []
bd_data = []
for da in bd_da:
    bd_data.append(da)
bd_data.append("其他")
for da2 in bd_ms[-10:]:
    ms_data.append(da2)
ms_data.append(bd_ms[0:-10].sum())
ms_data = np.array(ms_data)
su = ms_data.sum()
ms_data = ms_data/su
color = ('coral', 'g', 'r', 'c', 'm', 'y', 'seagreen', 'peru', 'pink', 'purple', 'lightgrey')
# pp.pie(ms_data, autopct="%1.1f%%", labels=bd_data, startangle=175, radius=1, colors=color)
# pp.title("十大品牌的市场占比")
# pp.axis("equal")

# 统计不同品牌的销售商家数
bd_n = data1.groupby(['brand'])['num'].sum().sort_values(ascending=True)
# bd_n[-15:].plot(kind="barh", title="品牌商家数排行")

# 购销比排行
buy_sales = data1["month_sales"]/data1["num"]
data1["buy_sales"] = buy_sales.astype(float)
b_s = data1.groupby(["brand"])["buy_sales"].mean().sort_values(ascending=True)
# b_s[-15:].plot(kind="barh", title="购销比排行")
n_da = bd_n[-15:].index
bd_data2 = []
for da in n_da:
    bd_data2.append(da)
bd_data2.remove("Newman/纽曼")
for i in b_s.index:
    if i not in bd_data2:
        b_s.drop(i, axis=0, inplace=True)
b_s[-15:].plot(kind="barh", title="购销比排行")

# 统计不同型号的销售商数
md_n = data1.groupby(["model"])["num"].sum().sort_values(ascending=True)
# md_n[-15:].plot(kind="barh", title="最受商家欢迎型号排行")

# 统计不同品牌的型号数
bd_md = data1.groupby(['brand'])['model'].count().sort_values(ascending=True)
# bd_md[-15:].plot(kind="barh", title="品牌型号数排行")

# 分析销量对销售商数的影响
num_list = data.values[3]   # 价格
num_list = np.array(list(map(int, num_list)))
# pp.plot(num_list, month_sales_list, "or")
# pp.title("销售商数-销量散点图")
# pp.ylabel("销量（部）")
# pp.xlabel("销售商数（家）")


# 分析不同手机品牌进军的价格区间(取销量前十名）
bd_pe = [[], [], [], [], [], [], [], [], [], []]
i = 0
for x in brand_list:
    for x2 in bd_data:
        if x == x2:
            bd_pe[bd_data.index(x)].append(price_list[i])
    i += 1
bd_pe_df = pda.DataFrame(
    [
        pda.Series(bd_pe[0]),
        pda.Series(bd_pe[1]),
        pda.Series(bd_pe[2]),
        pda.Series(bd_pe[3]),
        pda.Series(bd_pe[4]),
        pda.Series(bd_pe[5]),
        pda.Series(bd_pe[6]),
        pda.Series(bd_pe[7]),
        pda.Series(bd_pe[8]),
        pda.Series(bd_pe[9])
    ]
).T
bd_pe_df.columns = bd_da

# bd_pe_df.boxplot(vert=False)
# pp.title("十大品牌价格分布图")

# 分析不同内存手机的占比
ram_list = data.values[6].tolist()
ram_list = ",".join(ram_list).replace("内存", "")
ram_list = ram_list.replace("未获取,", "")
ram_list = ram_list.split(",")
ram_sum = len(ram_list)
ram_count = collections.Counter(ram_list)
ram_c = ram_count.most_common(7)
da = []
co = []
for dic in ram_c:
    da.append(dic[0])
    co.append(dic[1])
co_sum = np.array(co).sum()
other_sum = ram_sum - co_sum
da.append("其他")
co.append(other_sum)
co = (np.array(co))/ram_sum
# pp.pie(co, autopct="%1.1f%%", labels=da, startangle=90, radius=1)
# pp.axis("equal")
# pp.title("不同内存手机的市场占比")


# 分析不同屏幕尺寸手机的占比
def num(group):
    return np.size(group)


size_list = ','.join(data.values[7].tolist())
size_list = re.sub(u'[\u4E00-\u9FA5]', "", size_list)
size_list = re.sub("\,{2,8}", ",", size_list)
size_list = size_list.split(",")
size_list = pda.DataFrame(np.array(list(map(eval, size_list))), columns=["size"])
size_list2 = size_list["size"].copy()
size_list3 = size_list2.T.values
labels = ["4英寸以下", "4-5英寸", "5-5.5英寸", "5.5-6英寸", "6英寸以上"]
k = [0, 4, 5, 5.5, 6, size_list3.max()]
size_c = pda.cut(size_list3, k, labels=labels)
size_result = size_list.groupby(by=size_c)['size'].agg([num])
size_data = np.array(size_result.T.values[0])
# pp.pie(size_data, autopct="%1.1f%%", labels=labels, startangle=200, radius=1)
# pp.axis("equal")
# pp.title("不同尺寸手机的市场占比")

# 分析不同摄像机像素手机的占比
pixel_list = ','.join(data.values[8].tolist())
pixel_list = re.sub(u'[\u4E00-\u9FA5]', "", pixel_list)
pixel_list = re.sub("\,{2,8}", ",", pixel_list)
pixel_list = pixel_list.split(",")
pixel_list = pda.DataFrame(np.array(list(map(int, pixel_list))), columns=["pixel"])
pixel_list2 = pixel_list["pixel"].copy()
pixel_list3 = pixel_list2.T.values
labels = ["500万像素以下", "500-800万像素", "800-1200万像素", "1200-2000万像素", "2000万像素以上"]
k = [pixel_list3.min(), 500, 800, 1200, 2000, pixel_list3.max()]
pixel_c = pda.cut(pixel_list3, k, labels=labels)
pixel_result = pixel_list.groupby(by=pixel_c)['pixel'].agg([num])
pixel_data = np.array(pixel_result.T.values[0])
# pp.pie(pixel_data, autopct="%1.1f%%", labels=labels, startangle=120, radius=1)
# pp.axis("equal")
# pp.title("不同相机像素手机的市场占比")

# 分析不同核心数手机的占比
core_list = ','.join(data.values[9].tolist())
core_list = core_list.replace('真', "")
core_list = core_list.replace('未获取', "")
core_list = re.sub("\,{2,8}", ",", core_list)
core_list = core_list.split(",")
core_list = pda.DataFrame(np.array(core_list), columns=["pixel"])
core_result = core_list.groupby(['pixel'])['pixel'].agg([num]).sort_values(ascending=False, by='num')
core_sum = core_result.T.values.sum()
core_result2 = core_result[:6]
core_la = core_result2.T.columns.tolist()
core_la.append("其他")
core_sum2 = core_result2.T.values.sum()
otr_sum = core_sum - core_sum2
tran = core_result2.as_matrix().tolist()
tran.append([otr_sum])
core_result3 = np.array(tran)
core_result3 = core_result3/core_sum
# pp.pie(core_result3, autopct="%1.1f%%", labels=core_la, startangle=-10, radius=1)
# pp.axis("equal")
# pp.title("不同核心数手机的市场占比")

# 手机特点/卖点词云
'''
pic = imread("E:\\编程学习\\Project\\taobao\\timg.png")
wc = WordCloud(background_color='white',
               max_words=300,
               mask=pic,
               max_font_size=100,
               font_path="C:/Windows/Fonts/msyh.ttc",
               random_state=42,  # 为每个词返回一个PIL颜色
               )
tag = data.values[10].tolist()
for t in range(0, len(tag)):
    tag[t] = str(tag[t])
tag_data = ','.join(tag)
tag_data = jieba.cut(tag_data)
spd = open("E:\\编程学习\\Project\\taobao\\stopword.txt", "r")
stopword = spd.read()
tag_wd = []
for tag_w in tag_data:
    if tag_w.strip() not in stopword:
        tag_wd.append(tag_w)
tag_wd = " ".join(tag_wd)
spd.close()
wc.generate(tag_wd)
# pp.imshow(wc)
# pp.axis('off')
# 绘制词云
# pp.figure()
# pp.axis('off')
# 保存图片
# wc.to_file("E:\\编程学习\\Project\\taobao\\1.png")
'''
# 对价格、销量、销售商数进行聚类分析
'''
if __name__ == '__main__':
    kms = KMeans(n_clusters=3, n_jobs=2, max_iter=500)
    price_sales = kms.fit_predict(data1.iloc[:, 1:2].as_matrix())
    for i in range(0, len(price_sales)):
        if price_sales[i] == 0:
            pp.plot(data1.iloc[i:i+1, 3:4].as_matrix(), data1.iloc[i:i+1, 1:2].as_matrix(), "*r")
        elif price_sales[i] == 1:
            pp.plot(data1.iloc[i:i+1, 3:4].as_matrix(), data1.iloc[i:i+1, 1:2].as_matrix(), "sy")
        elif price_sales[i] == 2:
            pp.plot(data1.iloc[i:i+1, 3:4].as_matrix(), data1.iloc[i:i+1, 1:2].as_matrix(), "*k")
'''

# pp.show()
pp.savefig('E:\\编程学习\\Project\\taobao\\p17.png', format='png', bbox_inches='tight', transparent=True, dpi=800)
# transparent=True