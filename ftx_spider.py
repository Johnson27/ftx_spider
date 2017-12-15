# 房天下spider
# author: #27

# 目标：
# 爬取待售新房信息
# 1、爬取新房列表数据
# 包含：位置（区域）、状态、电话、户型图
# 2、每条新房对应该新房的动态列表
# 包含：预售、开盘、交房、包含价格信息的动态

# todo: 异常处理、异常监控、时间性能、数据库存储、分层、使用框架

import gzip
import re
from urllib import request
from io import BytesIO
from bs4 import BeautifulSoup

#房天下新房按区进行爬取
regions = ['pudong', 'baoshan', 'minhang', 'putuo', 'xuhui', 'yangpu', \
            'hongkou', 'huangpu', 'jingan', 'luwan', 'changning']
BASE_URL = 'http://newhouse.sh.fang.com'

spidered_list = []

# 获取新房list页面的大致信息
def spider_house_list(url):
    if url in spidered_list:
        return []
    spidered_list.append(url)
    house_lists = []
    html_bs4 = get_html_bs4(url)
    # 获取每个item实体
    list_items = html_bs4.find(id='newhouse_loupai_list').find_all('div', 'nlc_details')
    # 从每个item实体提取 名称、状态、价格、位置、电话
    for item in list_items:
        house_dict = {}
        house_dict['name'] = item.find('div', 'nlcd_name').a.string.strip()
        house_dict['status'] = item.find('div', 'fangyuan').span.string
        item_price = item.find('div', 'nhouse_price')
        house_dict['price'] = item_price.text.strip() if item_price else None
        house_dict['location'] = item.find('div', 'address').a['title']
        item_phone = item.find('div', 'tel')
        house_dict['phone'] = item_phone.p.text if item_phone else None 
        # 获取每个item的detail信息
        item_link = item.find('div', 'nlcd_name').a['href']
        house_detail = spider_house_detail(item_link)
        house_dict['news'] = house_detail['news']
        house_dict['size'] = house_detail['size']
        house_lists.append(house_dict)
    # 分页递归
    pages_root = html_bs4.find('div', 'page')
    if pages_root:
        next_page = pages_root.find('li', 'fr').find('a', 'next')
        if next_page:
            return (house_lists + spider_house_list(BASE_URL + next_page['href']))
        else:
            return house_lists
    return house_lists

# 获取新房详情信息：房型、动态
def spider_house_detail(url):
    house_detail = {}
    html_bs4 = get_html_bs4(url)
    house_detail['size'] = html_bs4.find('div', 'zlhx').text.strip()
    news_link = html_bs4.find('a', title=re.compile(r'动态$'))['href']
    house_detail['news'] = spider_detail_news(news_link)
    return house_detail

# 获取新房动态：动态、预售证、开盘
def spider_detail_news(url):
    house_news = {}
    html_bs4 = get_html_bs4(url)
    for info in ['blog', 'sale', 'open']:
        house_news[info] = []
        news_items_root = html_bs4.find(id='gushi_' + info)
        if(not news_items_root):
            continue
        news_items = news_items_root.find('ul', 'zs-list').find_all('li')
        for item in news_items:
            tmp_dict = {}
            tmp_dict['time'] = item.find('div', 'sLTime').text.strip()
            if info == 'blog':
                tmp_dict['title'] = item.h2.a.string
                tmp_dict['content'] = item.p.text.strip()
            elif info == 'sale':
                tmp_dict['content'] = item.find_all('p')[0].string
            else:
                pinfo = item.find_all('p')
                tmp_dict['content'] = pinfo[len(pinfo) - 1].string
            if info == 'sale':
                if tmp_dict not in house_news[info]:
                    house_news[info].append(tmp_dict)
            else:
                house_news[info].append(tmp_dict)
    return house_news   

def get_html_bs4(url):
    response = request.urlopen(url)
    if response.headers.get('Content-Encoding') == 'gzip':
        compressedData = response.read()
        compressedStream = BytesIO(compressedData)
        gzipper = gzip.GzipFile(fileobj=compressedStream)
        html = gzipper.read()
    else:
        html = response.read()
    html = BeautifulSoup(html, 'html.parser', from_encoding='gb2312')
    return html

if __name__ == '__main__':
    for region in regions:
        print('----------------------' + region + ' start---------------------\n')
        base_url = BASE_URL + '/house/s/' + region + '/a77-b82/'
        house_data = spider_house_list(base_url)
        print(house_data)
        print('----------------------' + region + ' end-----------------------\n')
        