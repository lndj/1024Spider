#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-04-25 23:21:33
# Project: 1024

from pyspider.libs.base_handler import *

import re
import os
import requests
from bs4 import BeautifulSoup
import time
import random

PAGE_START = 1
#default 30 pages
PAGE_END = 30
DIR_PATH = '/path/to/1024'

# Function to find a working URL through search
def find_working_url():
    search_terms = ["草榴社区", "1024 cl", "t66y"]
    search_url = "https://www.google.com/search?q="
    
    # Try different search terms
    for term in search_terms:
        try:
            # Add a random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            # Use a custom user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Perform the search
            response = requests.get(search_url + term, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            search_results = soup.find_all('a')
            potential_urls = []
            
            # Common domains used by the site
            known_domains = ['t66y.com', 'cl.', '1024', 'caoliu']
            
            # Check each result
            for result in search_results:
                href = result.get('href')
                if href and 'http' in href:
                    # Extract actual URL from Google redirect
                    if '/url?q=' in href:
                        href = href.split('/url?q=')[1].split('&')[0]
                    
                    # Check if this URL contains any of the known domains
                    if any(domain in href for domain in known_domains):
                        # Verify the URL is accessible
                        try:
                            test_response = requests.get(href, headers=headers, timeout=5)
                            if test_response.status_code == 200:
                                # Ensure URL ends with a slash
                                if not href.endswith('/'):
                                    href += '/'
                                potential_urls.append(href)
                        except:
                            continue
            
            # Return the first working URL found
            if potential_urls:
                return potential_urls[0]
                
        except Exception as e:
            print(f"Error searching with term '{term}': {str(e)}")
            continue
    
    # If no URL is found, return one of the known URLs as fallback
    return "http://t66y.com/"

# Try to find a working URL, otherwise use the default
try:
    URL = find_working_url()
    print(f"Using automatically found URL: {URL}")
except Exception as e:
    print(f"Error finding URL automatically: {str(e)}")
    # Fallback URLs
    URL = 'http://cl.comcl.org/'
    # Alternative URL
    # URL = 'http://t66y.com/'

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