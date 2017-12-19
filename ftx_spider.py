# 房天下spider
# author: #27

# 目标：
# 爬取待售新房信息
# 1、爬取新房列表数据
# 包含：位置（区域）、状态、电话、户型图
# 2、每条新房对应该新房的动态列表
# 包含：预售、开盘、交房、包含价格信息的动态

# todo: 数据库存储、分层、使用框架

import gzip
import time
import re
import threading
from urllib import request
from urllib import error
from io import BytesIO
from bs4 import BeautifulSoup

#房天下新房按区进行爬取
regions = ['pudong', 'baoshan', 'minhang', 'putuo', 'xuhui', 'yangpu', \
            'hongkou', 'huangpu', 'jingan', 'luwan', 'changning']
BASE_URL = 'http://newhouse.sh.fang.com'

lock = threading.Lock()

spidered_list = []

def do_spider_house_list(url):
    '''
    执行list spider
    '''
    if url in spidered_list:
        return []
    spidered_list.append(url)
    house_lists = []
    html_bs4 = get_html_bs4(url)
    if not html_bs4:
        return
    # 获取每个item实体
    list_items = html_bs4.find(id='newhouse_loupai_list').find_all('div', 'nlc_details')
    # 从每个item实体提取 名称、状态、价格、位置、电话
    threads = []
    for item in list_items:
        t = threading.Thread(target=spider_house_list, args=(item, house_lists))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # 分页递归
    pages_root = html_bs4.find('div', 'page')
    if pages_root:
        next_page = pages_root.find('li', 'fr').find('a', 'next')
        if next_page:
            return house_lists + do_spider_house_list(BASE_URL + next_page['href'])
        else:
            return house_lists
    return house_lists

def spider_house_list(item, house_lists):
    '''
    新房list信息提取
    '''
    print('%s is running' % threading.current_thread().name)
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
    print(house_dict)
    house_lists.append(house_dict)

def spider_house_detail(url):
    '''
    获取新房详情信息：房型、动态
    '''
    house_detail = {}
    html_bs4 = get_html_bs4(url)
    if not html_bs4:
        return
    house_detail['size'] = html_bs4.find('div', 'zlhx').text.strip()
    news_link = html_bs4.find('a', title=re.compile(r'动态$'))['href']
    house_detail['news'] = spider_detail_news(news_link)
    return house_detail

def spider_detail_news(url):
    '''
    获取新房动态：动态、预售证、开盘
    '''
    house_news = {}
    html_bs4 = get_html_bs4(url)
    if not html_bs4:
        return
    for info in ['blog', 'sale', 'open']:
        house_news[info] = []
        news_items_root = html_bs4.find(id='gushi_' + info)
        if not news_items_root:
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
    '''
    获取每个链接的BeautifulSoup格式化网页内容
    '''
    try:
        response = request.urlopen(url)
        if response.headers.get('Content-Encoding') == 'gzip':  # gzip压缩时先解压
            compressedData = response.read()
            compressedStream = BytesIO(compressedData)
            gzipper = gzip.GzipFile(fileobj=compressedStream)
            html = gzipper.read()
        else:
            html = response.read()
        html = BeautifulSoup(html, 'html.parser', from_encoding='gb2312')
    except (error.HTTPError, error.URLError) as e:
        print('读取url数据出现错误：', e)
        exception_write_log(url, e)
        return
    return html

def locker(func):
    '''
    锁decorator
    '''
    def wrapper(*args, **kw):
        lock.acquire()
        func(*args, **kw)
        lock.release()
    return wrapper

@locker
def exception_write_log(url, error):
    '''
    记录爬取过程中出错的url及错误
    '''
    f = open('exception_log.txt', 'a')
    line = '%s:\n%s\n' % (url, error)
    f.write(line)
    f.close()

@locker
def exception_log_clear():
    '''
    清空上次异常日志
    '''
    f = open('exception_log.txt', 'w')
    f.truncate()
    f.close()


if __name__ == '__main__':
    exception_log_clear()
    start_time = time.time()
    for region in regions:
        base_url = BASE_URL + '/house/s/' + region + '/a77-b82/'
        house_data = do_spider_house_list(base_url)
    end_time = time.time()
    print((end_time - start_time)/60)
        