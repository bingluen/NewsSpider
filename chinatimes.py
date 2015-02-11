# coding=UTF-8
# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import os

URL = 'http://www.chinatimes.com/history-by-date/'
NEWS_CONTENT_URL = 'http://www.chinatimes.com/newspapers/'
NEWS_REALTIME_URL = 'http://www.chinatimes.com/realtimenews/'
SOURE_TYPE = {'chinatimes': 2601, 'ctee': 2602, 'want': 2603, 'realtime': 2604}
HEADER = {'User_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
                'Accept': '"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'}

class NewsSpider:
    def __init__(self, soure, outputDirectory):
        self.soure = SOURE_TYPE[soure]
        self.outputDirectory = outputDirectory
        self.newsList = []
        self.limit = 0

    def setDate(self, date):
        ### format = yyyy-mm-dd
        self.date = date

    def setSoure(self, soure):
        self.soure = SOURE_TYPE[soure]

    def setDirectory(self, directory):
        self.outputDirectory = directory

    def setLimit(self, limit):
        self.limit = int(limit/11)+1

    def getNewsList(self):
        requester = requests.Session()
        ### first, get number of page of list
        if self.limit == 0:
            self.limit = self.getNewsListPage()
        ### getlist
        count = 1
        req_url = self.date+'-'+str(self.soure)
        for num in range (1, self.limit+1):
            r = requester.get(URL+req_url+'?page='+str(num))
            content = BeautifulSoup(r.text, 'html.parser')
            newsList = content.article.find_all('h2')
            for listItem in newsList:
                itemId = re.findall('([-0-9]+)', listItem.a['href'], re.S)[0]
                self.newsList.append(itemId)
            print u'catched list of page ' + str(count) +'/' + str(self.limit)
            count = count + 1


    def getNewsListPage(self):
        requester = requests.Session()
        req_url = self.date+'-'+str(self.soure)
        r = requester.get(URL+req_url)
        content = BeautifulSoup(r.text, 'html.parser')
        pag = content.find('div', class_='pagination clear-fix').find_all('li')
        page =  re.findall('page=([0-9]*)' ,pag[len(pag)-1].a['href'], re.S)[0]
        return int(page)

    def getNewsItemContent(self):
        requester = requests.Session()
        count = 0
        for newsItem in self.newsList:
            if self.soure != 2604:
                r = requester.get(NEWS_CONTENT_URL+newsItem)
            else:
                r = requester.get(NEWS_REALTIME_URL+newsItem)
            content = BeautifulSoup(r.text, 'html.parser')
            parserData = {}
            parserData['title'] = re.findall('([^\r\n ]+)', content.article.header.h1.string, re.S)[0]
            parserData['newsText'] = ''


            for newsContent in  content.article.find_all('p'):
                parserData['newsText'] = parserData['newsText'] + newsContent.text
            parserData['date'] = newsItem[0:4]+'-'+newsItem[4:6]+'-'+newsItem[6:8]

            page_index = content.article.ul.find_all('li')

            parserData['type'] = re.findall('([^\r\n ]+)', page_index[len(page_index)-1].span.string, re.S)[0]


            parserData['report'] = content.aside.find('div', class_='page_rp_box').find('div', class_='name').string

            self.output(parserData, count)
            print u'catched content of ' + str(count) + '/' + str(len(self.newsList))
            count = count + 1

    def output(self, newsContent, count, option = {}):
        if not os.path.exists(self.outputDirectory):
            os.mkdir(self.outputDirectory)
        if not os.path.exists(self.outputDirectory+'/'+newsContent['type']):
            os.mkdir(self.outputDirectory+'/'+newsContent['type'])

        f = open(self.outputDirectory+'/'+newsContent['type']+'/'+newsContent['date']+'_'+str(count)+'.txt', 'w')
        if not ('title' in option) or ('title' in option and option['title'] != False):
            ###print 'Title:'+newsContent['title']
            f.write('Title:'+newsContent['title'].encode('utf-8'))
            

        if not ('date' in option) or ('date' in option and opotion['date'] != False):
            ###print 'Date:'+newsContent['date']
            f.write('Date:'+newsContent['date'])
                
            

        if not ('type' in option) or ('type' in option and option['tpye'] != False):
            ###print 'Type:'+newsContent['type']
            f.write('Type:'+newsContent['type'].encode('utf-8'))

        if not ('report' in option) or ('report' in option and option['report'] != False):
            ###print 'Report:'+newsContent['report']
            f.write('Report:'+newsContent['report'].encode('utf-8'))
            


        if not ('content' in option) or ('content' in option and option['content'] != False):
            ###print 'Content:'+newsContent['newsText']
            f.write('Content:'+newsContent['newsText'].encode('utf-8'))

        f.close()

    def execute(self):
        self.newsList = []
        self.getNewsList()
        self.getNewsItemContent()


