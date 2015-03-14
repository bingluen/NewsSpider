# coding=UTF-8
# -*- coding: UTF-8 -*-

### news spider by Erickson Juang

### this module need request and beautifulsoup4

import requests
from bs4 import BeautifulSoup
import re
import os
import datetime

###define const

URL = {
	'chinatimes' : {
		'content' : {
			'newspaper' : 'http://www.chinatimes.com/newspapers/', 
			'realtime' : 'http://www.chinatimes.com/realtimenews/'
		},

		###
		# list url = list + yyyy-mm-dd + '-' + soure

		'list' : 'http://www.chinatimes.com/history-by-date/',
		'soure' : {
			'chinatimes': '2601',
			 'ctee': '2602', 
			 'want': '2603', 
			 'realtime': '2604'
		}
	},

	'ltn' : {
		'root': 'http://news.ltn.com.tw/',
		'list': {
			'newspaper': 'http://news.ltn.com.tw/newspaper/',
			'realtime' : 'http://news.ltn.com.tw/list/'
		},

		'soure': ['politics', 'society', 'local', 'life'
        , 'opinion', 'world', 'business', 'sports'
        , 'entertainment', 'consumer', 'supplement'
        , 'focus'],

        'content': {
        	'opinion' : 'http://talk.ltn.com.tw/article/paper/'
        	### Other use root + path which get by list
        }
	}
}

###Chinatimes news Spider###

class chinatimesSpider:
	def __init__(self):
		self.newsList = []
		self.date = ''
		self.soure = ''
		self.directory = ''

	def setDate(self, date):
		### format of date is yyyy-mm-dd
		try:
        	inputDate = datetime.datetime.strptime(date_text, '%Y-%m-%d')
    	except ValueError:
        	raise ValueError("Incorrect date format, should be YYYY-mm-dd")

        if inputDate > datetime.datetime.now()
        	raise ValueError("Incorrect date, is is bigger than now")

		self.date = date

	def setSoure(self, soure):
		try:
        	URL['chinatimes']['soure'][soure]
    	except KeyError:
        	raise KeyError("Incorrect news soure (only chinatimes / ctee / want / realtime)")

		self.soure = URL['chinatimes']['soure'][soure]

	def setDir(self, mDir):
		if not os.path.exists(mDir):
			try:
				os.mkdir(mdir)
			except OSError:
				raise OSError("Can't create folder, please check permission")
		self.directory = mDir

	def __getList(self):
		### get number of page of list
	
	def __getNumOfPageOfList(self):
		try:
			r = requests.get(URL['chinatimes']['list']+str(self.date)+'-'+URL['chinatimes']['soure'][self.soure])
		except requests.exceptions.ConnectionError:
			raise requests.exceptions.ConnectionError("連線失敗，請檢查網路連線狀態。")

		DOM = BeautifulSoup(r.text, 'html.parser')

		try:
			numPage = DOM.find('div', class_='pagination').find('li', class_='last')
		except Exception, e:
			raise

