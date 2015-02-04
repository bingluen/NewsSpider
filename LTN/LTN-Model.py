# coding=UTF-8
NEW_CLASS = ['politics', 'society', 'local', 'life'
        , 'opinion', 'world', 'business', 'sport'
        , 'entertainment', 'consumer', 'supplement'
        , 'focus']

URL = 'http://news.ltn.com.tw/news/opinion/paper/'
HEADER = {'User_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Accept': '"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'}

import requests
from bs4 import BeautifulSoup


class NewsSpider:
    def __init__(self, startID, endID):
        self.startId = startID
        self.endId = endID
        self.row = []
        self.result = []

    def getNewsRowContent(self):
        requester = requests.Session()
        for num in range(self.startId, self.endId):
            r = requester.get(URL+str(num), headers=HEADER)
            self.row.append(r.text)

    def parserNewsContent(self):
        parserContent = {}
        for rowContent in self.row:
            content = BeautifulSoup(rowContent, "lxml")
            parserContent['title'] = content.h1.string
            newsText = content.find(id="newstext")
            parserContent['newsDate'] = newsText.span.string
            parserContent['newsText'] = ''


            for newsContent in newsText.find_all('p'):
                parserContent['newsText'] = parserContent['newsText'] + newsContent.text
            ### get news type

            parserContent['type'] = content.select('div > .guide')[0].find_all('a')[1].string

            self.result.append(parserContent.copy())


    def outputResultAsFile(self):
        f = open('output.html', 'w')
        for news in self.result:
            print 'Title:' + news['title']
            print 'Date:' + news['newsDate']
            print 'Type:' + news['type']
            print 'Content:' + news['newsText']
            f.write(str(news))

        f.close()




spider = NewsSpider(853155, 853156)
spider.getNewsRowContent()
spider.parserNewsContent()
spider.outputResultAsFile()
