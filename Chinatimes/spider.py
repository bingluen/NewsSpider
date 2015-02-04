# coding=UTF-8
import requests
from bs4 import BeautifulSoup
import re

URL = 'http://www.chinatimes.com/history-by-date/'
NEWS_CONTENT_URL = 'http://www.chinatimes.com/newspapers/'
SOURE_TYPE = {'chinatimes': 2601, 'realtime': 2604}
HEADER = {'User_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
                'Accept': '"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'}

class NewsSpider:
    def __init__(self, soure):
        self.soure = SOURE_TYPE[soure]
        self.newsList = []
        self.newsDetail = []

    def setDate(self, date):
        ### format = yyyy-mm-dd
        self.date = date

    def setSoure(self, soure):
        self.soure = soure

    def getNewsList(self):
        requester = requests.Session()
        ### first, get number of page of list
        page = self.getNewsListPage()
        ### getlist
        req_url = self.date+'-'+str(self.soure)
        for num in range (1, page+1):
            r = requester.get(URL+req_url+'?page='+str(num))
            content = BeautifulSoup(r.text, 'lxml')
            newsList = content.article.find_all('h2')
            for listItem in newsList:
                itemId = re.findall('([-0-9]+)', listItem.a['href'], re.S)[0]
                self.newsList.append(itemId)

    def getNewsListPage(self):
        requester = requests.Session()
        req_url = self.date+'-'+str(self.soure)
        r = requester.get(URL+req_url)
        content = BeautifulSoup(r.text, 'lxml')
        pag = content.find('div', class_='pagination clear-fix').find_all('li')
        page =  re.findall('page=([0-9]*)' ,pag[len(pag)-1].a['href'], re.S)[0]
        return page

    def getNewsItemContent(self):
        requester = requests.Session()
        for newsItem in self.newsList:
            r = requester.get(NEWS_CONTENT_URL+newsItem)
            content = BeautifulSoup(r.text, 'lxml')
            parserData = {}
            parserData['title'] = re.findall('([^\r\n ]+)', content.article.header.h1.string, re.S)[0]
            parserData['newsText'] = ''


            for newsContent in  content.article.find_all('p'):
                parserData['newsText'] = parserData['newsText'] + newsContent.text
            parserData['date'] = newsItem[0:4]+'-'+newsItem[4:6]+'-'+newsItem[6:8]

            page_index = content.article.ul.find_all('li')

            parserData['type'] = re.findall('([^\r\n ]+)', page_index[len(page_index)-1].span.string, re.S)[0]


            parserData['report'] = content.aside.find('div', class_='page_rp_box').find('div', class_='name').string

            self.newsDetail.append(parserData.copy())



spider = NewsSpider('chinatimes')
spider.setDate('2015-01-28')
spider.getNewsList()
spider.getNewsItemContent()

print spider.newsDetail
