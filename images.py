#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-04-25 23:21:33
# Project: 1024

from pyspider.libs.base_handler import *

import re
import os

PAGE_START = 1
#默认抓取30页
PAGE_END = 30
DIR_PATH = '/path/to/1024'

#1024地址多变，自己找可用的咯
URL = 'http://cl.comcl.org/'
#URL = 'http://t66y.com/'
START_URL = URL + 'thread0806.php?fid=8'

class Handler(BaseHandler):
    crawl_config = {
    }
    def __init__(self):
        self.deal = Deal()
        self.page_num = PAGE_START
        self.page_total = PAGE_END
        
    @every(minutes=24 * 60)
    def on_start(self):
        while self.page_num <= self.page_total:
            url = START_URL + '&search=&page=' + str(self.page_num)
            self.crawl(url, callback=self.index_page)
            self.page_num += 1

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        pattern=re.compile(URL+'htm_data/*')
        for each in response.doc('h3 > a').items():
            match = pattern.match(each.attr.href)
            if match:
               self.crawl(each.attr.href, callback=self.detail_page,fetch_type='js')

    @config(priority=2)
    def detail_page(self, response):
        
        name=response.doc('#main > div:nth-child(4) > table > tbody > tr.tr1.do_not_catch > th:nth-child(2) > table > tbody > tr > td > h4').text()
        
        dir_path = self.deal.mkDir(name)
        
        if dir_path:
            imgs = response.doc('.do_not_catch > input[src^="http"]').items()
            count = 1                
            for img in imgs:
                url = img.attr.src
                if url:
                    extension = self.deal.getExtension(url)
                    file_name = name + str(count) + '.' + extension
                    count += 1
                    self.crawl(img.attr.src,callback=self.save_img,save={'dir_path': dir_path, 'file_name': file_name})
          
    def save_img(self, response):
        content = response.content
        dir_path = response.save['dir_path']
        file_name = response.save['file_name']
        file_path = dir_path + '/' + file_name
        self.deal.saveImg(content, file_path)
        

    
    
class Deal:
    def __init__(self):
        self.path = DIR_PATH
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)
 
    def mkDir(self, path):
        path = path.strip()
        dir_path = self.path + path
        exists = os.path.exists(dir_path)
        if not exists:
            os.makedirs(dir_path)
            return dir_path
        else:
            return dir_path
 
    def saveImg(self, content, path):
        f = open(path, 'wb')
        f.write(content)
        f.close()
 
    def saveBrief(self, content, dir_path, name):
        file_name = dir_path + "/" + name + ".txt"
        f = open(file_name, "w+")
        f.write(content.encode('utf-8'))
 
    def getExtension(self, url):
        extension = url.split('.')[-1]
        return extension