# coding=UTF-8
NEW_CLASS = ['politics', 'society', 'local', 'life'
        , 'opinion', 'world', 'business', 'sports'
        , 'entertainment', 'consumer', 'supplement'
        , 'focus']

URL = 'http://news.ltn.com.tw/'
HEADER = {'User_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Accept': '"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'}

import requests
from bs4 import BeautifulSoup
import os
import re

requester = requests.Session()

class NewsSpider:
    def __init__(self, outputDirectory):
        self.date = ''
        self.outputDirectory = outputDirectory
        self.list = []

    def setDate(self, date):
        self.date = date[0:4]+date[5:7]+date[8:10]

    def getList(self, newsType):
        newsList = []
        page = self.getNumOfPageOfList(newsType)
        for num in range(1, page+1):
            url = URL+'newspaper/'+newsType+'/'+self.date+'?page='+str(num)
            r = BeautifulSoup(requester.get(url, headers=HEADER).text, 'lxml')
            for listItem in r.find_all('li', class_='lipic'):
                newsList.append(listItem.a['href'][1:])
        self.list = newsList


    def getNumOfPageOfList(self, newsType):
        url = URL+'newspaper/'+newsType+'/'+self.date
        r = BeautifulSoup(requester.get(url, headers=HEADER).text, 'lxml')
        return int(re.findall(u'共有'+' ([0-9]+)', r.find_all('div', class_='tit')[0].string, re.S)[0])/20+1


    def getNewsContent(self, newsType):
        count = 1
        for item in self.list:
            r = requester.get(URL+item, headers=HEADER)
            parserContent = self.parserNewsContent(r.text)
            parserContent['type'] = newsType
            self.outputResultAsFile(parserContent, count)
            print "catched "+str(count)+' of '+ str(len(self.list))
            count = count + 1

    def parserNewsContent(self, rowContent):
        parserContent = {}
        content = BeautifulSoup(rowContent, "lxml")
        parserContent['title'] = content.h1.string
        newsText = content.find(id="newstext")
        parserContent['newsDate'] = newsText.span.string
        parserContent['newsText'] = ''


        for newsContent in newsText.find_all('p'):
            parserContent['newsText'] = parserContent['newsText'] + newsContent.text

        return parserContent


    def outputResultAsFile(self, newsContent, count, option = {}):
        ###print 'Title:' + news['title']
        ###print 'Date:' + news['newsDate']
        ###print 'Type:' + news['type']
        ###print 'Content:' + news['newsText']
        if not os.path.exists(self.outputDirectory):
            os.mkdir(self.outputDirectory)
        if not os.path.exists(self.outputDirectory+'/'+newsContent['type']):
            os.mkdir(self.outputDirectory+'/'+newsContent['type'])

        f = open(self.outputDirectory+'/'+newsContent['type']+'/'+newsContent['newsDate']+'_'+str(count)+'.txt', 'w')
        if not ('title' in option) or ('title' in option and option['title'] != False):
            ###print 'Title:'+newsContent['title']
            f.write('Title:'+newsContent['title'].encode('utf-8'))

        if not ('date' in option) or ('date' in option and opotion['date'] != False):
            ###print 'Date:'+newsContent['date']
            f.write('Date:'+newsContent['newsDate'])
                
        if not ('type' in option) or ('type' in option and option['tpye'] != False):
            ###print 'Type:'+newsContent['type']
            f.write('Type:'+newsContent['type'].encode('utf-8'))           


        if not ('content' in option) or ('content' in option and option['content'] != False):
            ###print 'Content:'+newsContent['newsText']
            f.write('Content:'+newsContent['newsText'].encode('utf-8'))

        f.close()

    def execute(self):
        for newsType in NEW_CLASS:
            print "catch News of " + newsType + ":"
            print "catch list of " + newsType + "...."
            self.getList(newsType)
            print "catch news content Total:"+ str(len(self.list))
            self.getNewsContent(newsType)
            print ''