# coding=UTF-8
# -*- coding: UTF-8 -*-

### news spider by Erickson Juang

### this module need request and beautifulsoup4

import requests
from bs4 import BeautifulSoup
import re
import os
import datetime
import codecs

###define const

URL = {
	'chinatimes' : {
		'root' : 'http://www.chinatimes.com/',

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
		'root': 'http://news.ltn.com.tw',
		'soure': {
			'newspaper': 'http://news.ltn.com.tw/newspaper/',
			'realtime' : 'http://news.ltn.com.tw/list/'
		},

		'type': ['politics', 'society', 'local', 'life'
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

class Chinatimes:
	"""docstring for Chinatimes"""
	def __init__(self):
		self.newsList = []
		self.date = ''
		self.soure = ''
		self.directory = ''

	def setDate(self, date):
		### format of date is yyyy-mm-dd
		try:
			inputDate = datetime.datetime.strptime(date, '%Y-%m-%d')
		except ValueError:
			raise ValueError("Incorrect date format, should be YYYY-mm-dd")

		if inputDate > datetime.datetime.now():
			raise ValueError("Incorrect date, is is bigger than now")

		self.date = date

	def setSoure(self, soure):
		try:
			URL['chinatimes']['soure'][soure]
		except KeyError:
			raise KeyError("Incorrect news soure (only chinatimes / ctee / want / realtime)")

		self.soure = soure

	def setDir(self, mDir):
		if not os.path.exists(mDir):
			try:
				os.mkdir(mDir)
			except OSError:
				raise OSError("Can't create folder, please check permission")
		self.directory = mDir

	def getList(self, page):
		newsList = []
		try:
			r = requests.get(URL['chinatimes']['list']+str(self.date)+'-'+URL['chinatimes']['soure'][self.soure]+'?page='+str(page))
		except requests.exceptions.ConnectionError:
			raise ListGetError( u"Error: 連線失敗，請檢查網路連線狀態。"+u"\nError: 無法取得 "+str(self.date)+self.soure+" 第 "+page+" 頁清單" + "\n\tSkip "+str(self.date)+' '+self.soure+' page ' +page)

		DOM = BeautifulSoup(r.text, 'html.parser')
		for item in DOM.article.find_all('h2'):
			newsList.append(item.a['href'])

		return newsList

	def getNumOfPageOfList(self):
		try:
			r = requests.get(URL['chinatimes']['list']+str(self.date)+'-'+URL['chinatimes']['soure'][self.soure])
		except requests.exceptions.ConnectionError:
			raise ListGetError("Error: can't connect"+u"\nError: 無法取得 "+str(self.date)+self.soure+" 之清單")

		DOM = BeautifulSoup(r.text, 'html.parser')

		try:
			pag = DOM.find('div', class_='pagination').find_all('li')
			numPage = int(re.findall('page=([0-9]+)', pag[len(pag) - 1].a['href'], re.S)[0])
		except TypeError:
			raise ParseError("Error: can't get number of page of list"+"\tSkip "+str(self.date)+' '+self.soure)
		return numPage

	def getContent(self, news):
		try:
			r = requests.get(URL['chinatimes']['root']+news)
		except requests.exceptions.ConnectionError:
			raise requests.exceptions.ConnectionError(u"Error: 連線失敗，請檢查網路連線狀態。"+"\n\tSkip "+URL['chinatimes']['root']+news)
		DOM = BeautifulSoup(r.text, 'html.parser')

		parseResult = {}

		
		try:
			#Get title
			parseResult['title'] = re.findall('([^ \t\n\r]+)', DOM.article.header.h1.string, re.S)[0]

			#Get date
			parseResult['date'] = DOM.time['datetime']

			#Get newsText
			parseResult['newsText'] = ''
			for text in DOM.article.article.find_all('p'):
				parseResult['newsText'] = parseResult['newsText'] + text.text

			#Get report
			report = DOM.find('div', class_='reporter').find('div', class_='rp_name')
			parseResult['report'] = report.text if report is not None else 'None'

			#Get type
			pag = DOM.article.ul.find_all('li')
			parseResult['type'] = re.findall('[^ \t\n\r]+', pag[len(pag) - 1].text, re.S)[0]

		except TypeError:
			raise ParseError( "Error: can't parse the news - "+URL['chinatimes']['root']+news)

		return parseResult

	def writeToFile(self, data, fileName):

		"""
			if you want output file to different folder by news type, do follow step
			remove comment in line 177, 183 and 184
			add comment in line 185
		"""

		"""
		if not os.path.exists(self.directory+'/'+data['type']):
			try:
				os.mkdir(self.directory+'/'+data['type'])
			except OSError:
				raise OSError("Can't create folder, please check permission")
		"""	
		#f = open(self.directory+'/'+data['type']+'/'+data['date'][0:4]+'-'+data['date'][5:7]+'-'+data['date'][8:10]+'_'+str(count)+'.txt', 'w')
		f = codecs.open(self.directory+'/'+fileName+'.txt', 'w', 'utf-8')
		fXml = codecs.open(self.directory+'/'+fileName+'.xml', 'w', 'utf-8')
		f.write(u'\ufeff')
		fXml.write(u'\ufeff')
		f.write('Title:'+data['title'].encode('utf-8')+'\n\r')
		f.write('Date:'+data['date']+'\n\r')
		f.write('Type:'+data['type'].encode('utf-8')+'\n\r')
		f.write('Report:'+data['report'].encode('utf-8')+'\n\r')
		f.write('Content:'+data['newsText'].encode('utf-8')+'\n\r')
		f.close()

		## XML output
		fXml.write('<ID>'+str(count)+'</ID>\n\r')
		fXml.write('<Category>'+data['type'].encode('utf-8')+'</Category>>\n\r')
		fXml.write('<Date>'+data['date']+'</Date>>\n\r')
		fXml.write('<Author1>'+data['report'].encode('utf-8')+'</Author1>>\n\r')
		fXml.write('<Title>'+data['title'].encode('utf-8')+'</Title>>\n\r')
		fXml.write('<Content>'+data['newsText'].encode('utf-8')+'</Content>>\n\r')
		fXml.close()

class ltnSpider:
	def __init__(self):
		self.date = ''
		self.soure = ''
		self.directory = ''

	def setDate(self, date):
		### format of date is yyyy-mm-dd
		try:
			inputDate = datetime.datetime.strptime(date, '%Y-%m-%d')
		except ValueError:
			raise ValueError("Incorrect date format, should be YYYY-mm-dd")

		if inputDate > datetime.datetime.now():
			raise ValueError("Incorrect date, is is bigger than now")

		self.date = date[0:4]+date[5:7]+date[8:10]

	def setSoure(self, soure):
		try:
			URL['ltn']['soure'][soure]
		except KeyError:
			raise KeyError("Incorrect news soure (only newspaper /  realtime)")

		self.soure = soure

	def setDir(self, mDir):
		if not os.path.exists(mDir):
			try:
				os.mkdir(mDir)
			except OSError:
				raise OSError("Can't create folder, please check permission")
		self.directory = mDir

	def getList(self, mType, page):

		newsList = []
		if self.soure == "newspaper":
			try:
				r = requests.get(URL['ltn']['soure']['newspaper']+mType+'/'+str(self.date)+'?page='+str(page))
			except requests.exceptions.ConnectionError:
				raise requests.exceptions.ConnectionError(u"Error: 連線失敗，請檢查網路連線狀態。"+u"Error: 無法取得 "+str(self.date)+self.soure+" 第 "+page+" 頁清單")

			DOM = BeautifulSoup(r.text, 'html.parser')
			for item in DOM.find('ul', id='newslistul').find_all('li'):
				newsList.append(item.a['href'])
			return newsList

		if self.soure == "realtime":
			try:
				r = requests.get(URL['ltn']['soure']['realtime']+mType+'?page='+str(page))
			except requests.exceptions.ConnectionError:
				raise requests.exceptions.ConnectionError(u"Error: 連線失敗，請檢查網路連線狀態。"+u"Error: 無法取得 "+str(self.date)+self.soure+" 第 "+page+" 頁清單")
			
			DOM = BeautifulSoup(r.text, 'html.parser')
			for item in DOM.find('ul', id='newslistul').find_all('li'):
				newsList.append(item.a['href'])

			return newsList

	def getNumOfPageOfList(self, mType):
		if self.soure == "newspaper":
			
			try:
				r = requests.get(URL['ltn']['soure']['newspaper']+mType+'/'+str(self.date))
			except requests.exceptions.ConnectionError:
				raise requests.exceptions.ConnectionError(u"Error: 連線失敗，請檢查網路連線狀態。")

			DOM = BeautifulSoup(r.text, 'html.parser')

			try:
				pag = DOM.find('div', class_='list').find('div', class_='tit')
				num = int(re.findall(u'共有 ([0-9]+) 筆', pag.text, re.S)[0])
				numPage = num / 20 if num%20 == 0 else num / 20  + 1
			except TypeError:
				raise ParseError(u"Error: 無法取得 "+str(self.date)+self.soure+" 之清單列表頁數")

		if self.soure == "realtime":

			try:
				r = requests.get(URL['ltn']['soure']['realtime']+mType)
			except requests.exceptions.ConnectionError:
				raise requests.exceptions.ConnectionError("Error: can't connect" + u"\nError: 無法取得 "+str(self.date)+self.soure+" 之清單")

			DOM = BeautifulSoup(r.text, 'html.parser')

			

			try:
				pag = DOM.find('div', id='page').find_all('a')
				numPage = int(re.findall('page=([0-9]+)', pag[len(pag) - 1]['href'], re.S)[0])
			except TypeError:
				raise TypeError(u"Error: 無法取得 ", str(self.date)+' '+self.soure, u" 之清單列表"+"\nSkip "+str(self.date)+' '+self.soure)


		return numPage



	def getContent(self, news):
		try:
			r = requests.get(URL['ltn']['root']+news)
		except requests.exceptions.ConnectionError:
			raise requests.exceptions.ConnectionError(u"Error: 連線失敗，請檢查網路連線狀態。"+"\tSkip "+URL['ltn']['root']+news)

		DOM = BeautifulSoup(r.text, 'html.parser')

		parseResult = {}

		if len(re.findall('opinion', news, re.S)) > 0:

			##言論的page跟人加不一樣(；´Д｀)
				
			try:
				content = DOM.find('div', class_='content').find('div', class_='conbox')

				#Get title
				parseResult['title'] = content.h1.text

				#Get date
				parseResult['date'] = re.sub('[\n\r\t]', '', content.find('div', class_='writer').text)

				#Get newsText
				parseResult['newsText'] = ''
				for text in content.find('div', class_='cont').find_all('p'):
					parseResult['newsText'] = parseResult['newsText'] + text.text

				#Get type
				parseResult['type'] = u'言論'

			except TypeError:
				raise ParseError( "Error: can't parse the news - "+URL['ltn']['root']+news)


		elif len(re.findall('entertainment', news, re.S)) > 0:
			##娛樂的page跟人加不一樣(；´Д｀)
			try:
				content = DOM.find('div', class_='news_content')

				#Get title
				parseResult['title'] = content.find('div', class_='Btitle').text

				#Get date
				parseResult['date'] = content.find('div', class_='date').text

				#Get newsText
				parseResult['newsText'] = ''
				for text in content.find_all('p'):
					parseResult['newsText'] = parseResult['newsText'] + text.text

				#Get type
				parseResult['type'] = u'娛樂'

			except TypeError:
				raise ParseError( "ParseError: can't parse the news - "+URL['ltn']['root']+news)


		else:

			try: 	

				#Get title
				parseResult['title'] = DOM.find('div', class_='content').h1.text

				#Get date
				parseResult['date'] = DOM.find('div', id='newstext').span.text

				#Get newsText
				parseResult['newsText'] = ''
				for text in DOM.find('div', id='newstext').find_all('p'):
					parseResult['newsText'] = parseResult['newsText'] + text.text

				#Get type 
				if len(re.findall('local', news, re.S)) > 0:
					parseResult['type'] = u'地方新聞'
				else:
					pag = DOM.find('div', class_='guide').find_all('a')
					parseResult['type'] = pag[len(pag)-1].text

			except TypeError:
				raise ParseError( "ParseError: can't parse the news - "+URL['ltn']['root']+news)
				

			except AttributeError:
				raise ParseError( "ParseError: can't parse the news - "+URL['ltn']['root']+news)
		return parseResult

	def writeToFile(self, data, fileName):
		"""
			if you want output file to different folder by news type, do follow step
			remove comment in line 370, 376 and 377
			add comment in line 378

			Action
				if output folder by news type, the count of some type will not start from 1
		"""

		"""
		if not os.path.exists(self.directory+'/'+data['type']):
			try:
				os.mkdir(self.directory+'/'+data['type'])
			except OSError:
				raise OSError("Can't create folder, please check permission")
		"""	
		#f = open(self.directory+'/'+data['type']+'/'+data['date']+'_'+str(count)+'.txt', 'w')
		date = re.findall('([0-9]+)', data['date'], re.S)
		f = codecs.open(self.directory+'/'+fileName+'.txt', 'w', 
			'utf-8')
		f.write(u'\ufeff')
		fXml = codecs.open(self.directory+'/'+fileName+'.xml', 'w', 'utf-8')
		fXml.write(u'\ufeff')
		f.write('Title:'+data['title']+'\n\r')
		f.write('Date:'+data['date'].encode('utf-8')+'\n\r')
		f.write('Type:'+data['type']+'\n\r')
		f.write('Content:'+data['newsText']+'\n\r')
		f.close()

		## XML output
		fXml.write('<ID>'+str(self.count)+'</ID>\n\r')
		fXml.write('<Category>'+data['type']+'</Category>>\n\r')
		fXml.write('<Date>'+data['date']+'</Date>>\n\r')
		fXml.write('<Title>'+data['title']+'</Title>>\n\r')
		fXml.write('<Content>'+data['newsText']+'</Content>>\n\r')
		fXml.close()


class ListGetError:
	def __init__(self, arg):
		self.messages = arg

class ParseError:
	def __init__(self, arg):
		self.messages = arg