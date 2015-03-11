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
import string

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
        if page == 0:
            return 0
        for num in range(1, page+1):
            url = URL+'newspaper/'+newsType+'/'+self.date+'?page='+str(num)
            r = BeautifulSoup(requester.get(url, headers=HEADER).text, 'html.parser')
            for listItem in r.find_all('li', class_='lipic'):
                newsList.append(listItem.a['href'][1:])
        self.list = newsList


    def getNumOfPageOfList(self, newsType):
        url = URL+'newspaper/'+newsType+'/'+self.date
        r = BeautifulSoup(requester.get(url, headers=HEADER).text, 'html.parser')
        count = re.findall(u'共有'+' ([0-9]+)', r.find_all('div', class_='tit')[0].string, re.S)
        if len(count) == 0:
            print u'Error: can\'t catch news list of date:' + self.date + ' newstype:' + newsType
            return 0
        return int(count[0])/20+1


    def getNewsContent(self, newsType):
        count = 1
        print 'Type = '+newsType+', Total = '+str(len(self.list))
        for item in self.list:
            r = requester.get(URL+item, headers=HEADER)
            parserContent = self.parserNewsContent(r.text)
            if parserContent == False:
                print "Error: parse "+str(count)+' / '+ str(len(self.list)) + " failed, in type: " + newsType + ' date: ' + self.date
                count = count + 1
                continue;
            parserContent['type'] = newsType
            self.outputResultAsFile(parserContent, count)
            count = count + 1

    def parserNewsContent(self, rowContent):
        parserContent = {}
        content = BeautifulSoup(rowContent, "html.parser")
        if content.h1 is None:
            return False
        parserContent['title'] = content.h1.string
        newsText = content.find(id="newstext")
        if newsText is None:

            newsText = content.find_all('div', class_='content')[0]
            parserContent['newsDate'] = filter(lambda x: x in string.printable, newsText.find_all('div', class_='writer')[0].span.string).replace(':', '_')
            parserContent['newsText'] = ''
            for newsContent in newsText.find_all('div', class_='cont')[0].find_all('p'):
                parserContent['newsText'] = parserContent['newsText'] + newsContent.text
            return parserContent

            if newsText is None:
                return False
        parserContent['newsDate'] = filter(lambda x: x in string.printable, newsText.span.text).replace(':', '_')

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
            f.write('Title:'+newsContent['title'].encode('utf-8')+'\n\r')

        if not ('date' in option) or ('date' in option and opotion['date'] != False):
            ###print 'Date:'+newsContent['date']
            f.write('Date:'+newsContent['newsDate']+'\n\r')
                
        if not ('type' in option) or ('type' in option and option['tpye'] != False):
            ###print 'Type:'+newsContent['type']
            f.write('Type:'+newsContent['type'].encode('utf-8')+'\n\r')           


        if not ('content' in option) or ('content' in option and option['content'] != False):
            ###print 'Content:'+newsContent['newsText']
            f.write('Content:'+newsContent['newsText'].encode('utf-8')+'\n\r')

        f.close()

    def execute(self):
        print "catch ltn history News"
        for newsType in NEW_CLASS:
            if self.getList(newsType) != 0:
                self.getNewsContent(newsType)

s = NewsSpider('ltn')
s.setDate('2015-03-10')
s.getList('opinion')
s.getNewsContent('opinion')