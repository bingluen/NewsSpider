# coding=UTF-8
# -*- coding: UTF-8 -*-

### news spider by Erickson Juang

### this module need request and beautifulsoup4
import sys
import requests
from bs4 import BeautifulSoup
import re
import os
import datetime
import codecs

###define const

URL = {
	'chinatimes' : {
		'root' : 'http://www.chinatimes.com',

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


proxy = {
	"http": "http://proxy.hinet.net:80",
	"https": "https://proxy.hinet.net:80"
}

###Chinatimes news Spider###

class chinatimesSpider:
	def __init__(self):
		self.newsList = []
		self.date = ''
		self.soure = ''
		self.directory = ''
		self.logFile = codecs.open("chinatimes-NewsSpider-log-"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))+".txt", "w", "utf-8")
		self.logFile.write(u'\ufeff')
		self.logListFile = codecs.open("chinatimes-NewsSpider-log-List-"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))+".csv", "w", "utf-8")
		self.logListFile.write(u'\ufeff')
		self.ReportLog = codecs.open("[Research&Development]chinatimes-NewsSpider-ReportLog-"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))+".txt", "w", "utf-8")
		self.ReportLog.write(u'\ufeff')

		if not os.path.exists('chinatimes/'):
			try:
				os.mkdir('chinatimes/')
			except OSError:
				raise OSError("Can't create folder, please check permission")

	def __del__(self):
		self.logFile.close()
		self.logListFile.close()
		self.ReportLog.close()

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
		if not os.path.exists('chinatimes/'+mDir):
			try:
				os.mkdir('chinatimes/'+mDir)
			except OSError:
				raise OSError("Can't create folder, please check permission")
		self.directory = 'chinatimes/'+mDir

	def __getList(self):
		### get number of page of list
		try:
			numPage = self.__getNumOfPageOfList()
		except requests.exceptions.ConnectionError:
			raise ( "\tSkip "+str(self.date)+' '+self.soure)
			return
		except TypeError:
			return
		
		for page in range(1, numPage+1):
			try:
				r = requests.get(URL['chinatimes']['list']+str(self.date)+'-'+URL['chinatimes']['soure'][self.soure]+'?page='+str(page), proxies=proxy)
			except requests.exceptions.ConnectionError:
				self.logFile.write( u"Error: 連線失敗，請檢查網路連線狀態。"+'\r\n')
				self.logFile.write( u"Error: 無法取得 "+str(self.date)+self.soure+" 第 "+page+" 頁清單"+'\r\n')
				continue

			DOM = BeautifulSoup(r.text, 'html.parser')
			for item in DOM.article.find_all('h2'):
				self.newsList.append(item.a['href'])

	
	def __getNumOfPageOfList(self):
		try:
			r = requests.get(URL['chinatimes']['list']+str(self.date)+'-'+URL['chinatimes']['soure'][self.soure], proxies=proxy)
		except requests.exceptions.ConnectionError:
			self.logFile.write( u"Error: 連線失敗，請檢查網路連線狀態。"+'\r\n')
			self.logFile.write("Error: can't connect"+u"\nError: 無法取得 "+str(self.date)+self.soure+" 之清單")

		DOM = BeautifulSoup(r.text, 'html.parser')

		try:
			pag = DOM.find('div', class_='pagination').find_all('li')
			numPage = int(re.findall('page=([0-9]+)', pag[len(pag) - 1].a['href'], re.S)[0])
		except TypeError:
			self.logFile.write( u"Error: 無法取得 "+str(self.date)+self.soure+" 之清單列表"+'\r\n')
			self.logFile.write( "\tSkip "+str(self.date)+' '+self.soure+'\r\n')
			self.logFile.write("Error: can't get list"+"\tSkip "+str(self.date)+' '+self.soure)

		return numPage

	def __getContent(self):
		for news in self.newsList:
			try:
				r = requests.get(URL['chinatimes']['root']+news, proxies=proxy)
			except requests.exceptions.ConnectionError:
				self.logFile.write( u"Error: 連線失敗，請檢查網路連線狀態。"+'\r\n')
				self.logFile.write( "\tSkip "+URL['chinatimes']['root']+news+'\r\n')
				raise requests.exceptions.ConnectionError(u"Error: 連線失敗，請檢查網路連線狀態。"+"\n\tSkip "+URL['chinatimes']['root']+news)
			DOM = BeautifulSoup(r.text, 'html.parser')

			parseResult = {}

			parseResult['url'] = URL['chinatimes']['root']+news
			
			try:
				#Get title
				#print(DOM.article.header.h1.string)
				parseResult['title'] = re.findall('([^ \n\t\r][^\n\t\r]+)', DOM.article.header.h1.string, re.S)[0]
				#parseResult['title'] = DOM.article.header.h1.string
			except TypeError:
				self.logFile.write( "Error: can't parse title of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue
			except AttributeError:
				self.logFile.write( "Error: can't parse title of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			except IndexError:
				self.logFile.write( "Error: can't parse title of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			try:
				#Get date
				dateInfo = re.findall('([0-9]{4})\/([0-9]{2})\/([0-9]{2})', DOM.time['datetime'], re.S)[0]
				parseResult['date'] = dateInfo[0]+dateInfo[1]+dateInfo[2]
			except TypeError:
				self.logFile.write( "Error: can't parse date of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue
			except AttributeError:
				self.logFile.write( "Error: can't parse date of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			except IndexError:
				self.logFile.write( "Error: can't parse date of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			try:
				#Get time
				parseResult['time'] = re.findall('([0-9]{2}:[0-9]{2})', DOM.time.text, re.S)[0]
			except TypeError:
				self.logFile.write( "Error: can't parse time of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue
			except AttributeError:
				self.logFile.write( "Error: can't parse time of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			except IndexError:
				self.logFile.write( "Error: can't parse time of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			try:
				#Get newsText
				parseResult['newsText'] = ''
				for text in DOM.article.article.find_all('p'):
					parseResult['newsText'] = parseResult['newsText'] + text.text
			except TypeError:
				self.logFile.write( "Error: can't parse newsText of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue
			except AttributeError:
				self.logFile.write( "Error: can't parse newsText of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			except IndexError:
				self.logFile.write( "Error: can't parse newsText of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			try:
				#Get report
				report = DOM.find('div', class_='reporter').find('div', class_='rp_name')
				parseResult['report'] = report.text if report is not None else ''
				parseResult['report'] = parseResult['report'].replace('')
				parseResult['report'] = parseResult['report'].split(u'、')
			except TypeError:
				self.logFile.write( "Error: can't parse author of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue
			except AttributeError:
				self.logFile.write( "Error: can't parse author of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			except IndexError:
				self.logFile.write( "Error: can't parse author of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			try:
				#Get type
				pag = DOM.article.ul.find_all('li')
				parseResult['type'] = re.findall('[^ \t\r\n]+', pag[len(pag) - 1].text, re.S)[0]
			except TypeError:
				self.logFile.write( "Error: can't parse type of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue
			except AttributeError:
				self.logFile.write( "Error: can't parse type of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			except IndexError:
				self.logFile.write( "Error: can't parse type of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			try:
				#Get click
				click = DOM.find('div', class_='art_click').find('span', class_='num')
				parseResult['click'] = click.text if click is not None else 'None'
			except TypeError:
				self.logFile.write( "Error: can't parse click number of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue
			except AttributeError:
				self.logFile.write( "Error: can't parse click number of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			except IndexError:
				self.logFile.write( "Error: can't parse click number of the news - "+URL['chinatimes']['root']+news + '\r\n')
				continue

			self.__writeToFile(parseResult, self.newsList.index(news))

	def __writeToFile(self, data, count):

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
		f = codecs.open(self.directory+'/'+data['date']+'_'+str(count)+'.txt', 'w', 'utf-8')
		fXml = codecs.open(self.directory+'/'+data['date']+'_'+str(count)+'.xml', 'w', 'utf-8')
		f.write(u'\ufeff')
		fXml.write(u'\ufeff')
		
		f.write(u'Url:'+data['url']+'\r\n')
		f.write(u'Title:'+data['title']+'\r\n')
		f.write('Time:'+data['time']+'\r\n')
		f.write('Date:'+data['date']+'\r\n')
		f.write(u'ClickNo:'+data['click']+'\r\n')
		f.write(u'Category:'+data['type']+'\r\n')
		f.write(u'Author:')
		for report in data['report']:
			f.write(report+' ')
		f.write('\r\n')
		f.write(u'Content:'+data['newsText']+'\r\n')
		f.close()

		## XML output
		fXml.write('<Article>\r\n')
		fXml.write(u'<Url>'+data['url']+'<Url>\r\n')
		fXml.write('<ID>'+str(count)+'</ID>\r\n')
		fXml.write(u'<Category>'+data['type']+'</Category>\r\n')
		fXml.write('<Time>'+data['time']+'</Time>\r\n')
		fXml.write('<Date>'+data['date']+'</Date>\r\n')
		fXml.write(u'<ClickNo>'+data['click']+'</ClickNo>\r\n')
		fXml.write('<Authors>\r\n')
		for report in data['report']:
			fXml.write(u'<Author>'+report+'</Author>\r\n')
		fXml.write('</Authors>\r\n')
		fXml.write(u'<Title>'+data['title']+'</Title>\r\n')
		fXml.write(u'<Content>'+data['newsText']+'</Content>\r\n')
		fXml.write('</Article>')
		fXml.close()

		#listLog
		self.logListFile.write(self.directory+'/'+data['date']+'_'+str(count)+'.xml'+','+str(count)+','+data['title']+','+data['date']+','+data['type']+',')
		for report in data['report']:
			self.logListFile.write(report+' ')
			self.ReportLog.write(report+' ')
		self.logListFile.write('\r\n')
		self.ReportLog.write('\r\n')

	def execute(self):
		self.logFile.write( "Catch "+self.date+" from soure = "+self.soure+" of chinatimes"+'\r\n')
		#empty news list
		self.newsList = []
		self.__getList()
		self.__getContent()

class ltnSpider:
	def __init__(self):
		self.newsList = []
		self.date = ''
		self.soure = ''
		self.directory = ''
		self.count = 0
		self.logFile = codecs.open("ltn-NewsSpider-log-"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))+".txt", "w", "utf-8")
		self.logListFile = codecs.open("ltn-NewsSpider-log-list-"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))+".csv", "w", "utf-8")
		self.logFile.write(u'\ufeff')
		self.logListFile.write(u'\ufeff')
		self.ReportLog = codecs.open("[Research&Development]ltn-NewsSpider-ReportLog-"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))+".txt", "w", "utf-8")
		self.ReportLog.write(u'\ufeff')

		if not os.path.exists('ltn'):
			try:
				os.mkdir('ltn')
			except OSError:
				raise OSError("Can't create folder, please check permission")

	def __del__(self):
		self.logFile.close()
		self.logListFile.close()
		self.ReportLog.close()

	def setDate(self, date):
		### format of date is yyyy-mm-dd
		try:
			inputDate = datetime.datetime.strptime(date, '%Y-%m-%d')
		except ValueError:
			raise ValueError("Incorrect date format, should be YYYY-mm-dd")

		if inputDate > datetime.datetime.now():
			raise ValueError("Incorrect date, is is bigger than now")

		self.date = date[0:4]+date[5:7]+date[8:10]
		self.count = 0

	def setSoure(self, soure):
		try:
			URL['ltn']['soure'][soure]
		except KeyError:
			raise KeyError("Incorrect news soure (only newspaper /  realtime)")
		self.count = 0
		self.soure = soure

	def setDir(self, mDir):
		if not os.path.exists('ltn/'+mDir):
			try:
				os.mkdir('ltn/'+mDir)
			except OSError:
				raise OSError("Can't create folder, please check permission")
		self.directory = 'ltn/'+mDir

	def __getList(self):
		if self.soure == "newspaper":
			for mType in URL['ltn']['type']:
				try:
					numPage = self.__getNumOfPageOfList(mType)
				except requests.exceptions.ConnectionError:
					self.logFile.write( "\tSkip "+str(self.date)+' '+self.soure+'\r\n')
					return
				except TypeError:
					return

				for page in range(1, numPage+1):
					try:
						r = requests.get(URL['ltn']['soure']['newspaper']+mType+'/'+str(self.date)+'?page='+str(page), proxies=proxy)
					except requests.exceptions.ConnectionError:
						self.logFile.write( u"Error: 連線失敗，請檢查網路連線狀態。"+'\r\n')
						self.logFile.write( u"Error: 無法取得 "+str(self.date)+self.soure+u" 第 "+page+u" 頁清單"+'\r\n')
						self.logFile.write( "\tSkip "+str(self.date)+' '+self.soure+' page ' +page+'\r\n')
						continue

					DOM = BeautifulSoup(r.text, 'html.parser')
					for item in DOM.find('ul', id='newslistul').find_all('li'):
						self.newsList.append(item.a['href'])

		if self.soure == "realtime":
			
			for mType in URL['ltn']['type']:
				try:
					numPage = self.__getNumOfPageOfList(mType)
				except requests.exceptions.ConnectionError:
					self.logFile.write( "\tSkip "+str(self.date)+' '+self.soure+'\r\n')
					return
				except TypeError:
					return

				for page in range(1, numPage+1):
					try:
						r = requests.get(URL['ltn']['soure']['realtime']+mType+'?page='+str(page), proxies=proxy)
					except requests.exceptions.ConnectionError:
						self.logFile.write( u"Error: 連線失敗，請檢查網路連線狀態。"+'\r\n')
						self.logFile.write( u"Error: 無法取得 "+str(self.date)+self.soure+u" 第 "+str(page)+u" 頁清單"+'\r\n')
						self.logFile.write( "\tSkip "+str(self.date)+' '+self.soure+' page ' +str(page)+'\r\n')
						continue

					DOM = BeautifulSoup(r.text, 'html.parser')
					for item in DOM.find('ul', id='newslistul').find_all('li'):
						self.newsList.append(item.a['href'])


	def __getNumOfPageOfList(self, mType):
		if self.soure == "newspaper":
			
			try:
				r = requests.get(URL['ltn']['soure']['newspaper']+mType+'/'+str(self.date), proxies=proxy)
			except requests.exceptions.ConnectionError:
				self.logFile.write( u"Error: 連線失敗，請檢查網路連線狀態。"+'\r\n')
				self.logFile.write( u"Error: 無法取得 "+str(self.date)+self.soure+u" 之清單"+'\r\n')
				raise requests.exceptions.ConnectionError("Error: can't connect")

			DOM = BeautifulSoup(r.text, 'html.parser')

			try:
				pag = DOM.find('div', class_='list').find('div', class_='tit')
				num = int(re.findall(u'共有 ([0-9]+) 筆', pag.text, re.S)[0])
				numPage = num / 20 if num%20 == 0 else num / 20  + 1
			except TypeError:
				self.logFile.write( u"Error: 無法取得 "+str(self.date)+self.soure+u" 之清單列表"+'\r\n')
				self.logFile.write( "\tSkip "+str(self.date)+' '+self.soure+'\r\n')
				raise TypeError("Can't getlist")

		if self.soure == "realtime":

			try:
				r = requests.get(URL['ltn']['soure']['realtime']+mType, proxies=proxy)
			except requests.exceptions.ConnectionError:
				self.logFile.write( u"Error: 連線失敗，請檢查網路連線狀態。"+'\r\n')
				self.logFile.write( u"Error: 無法取得 "+str(self.date)+self.soure+u" 之清單"+'\r\n')
				raise requests.exceptions.ConnectionError("Error: can't connect" + u"\nError: 無法取得 "+str(self.date)+self.soure+u" 之清單")

			DOM = BeautifulSoup(r.text, 'html.parser')

			

			try:
				pag = DOM.find('div', id='page').find_all('a')
				numPage = int(re.findall('page=([0-9]+)', pag[len(pag) - 1]['href'], re.S)[0])
			except TypeError:
				self.logFile.write( u"Error: 無法取得 ", str(self.date)+' '+self.soure, u" 之清單列表"+'\r\n')
				self.logFile.write( "\tSkip "+str(self.date)+' '+self.soure+'\r\n')
				raise TypeError("Can't getlist")


		return numPage

	def __getContent(self):
		lastData = {}
		for news in self.newsList:
			try:
				r = requests.get(URL['ltn']['root']+news, proxies=proxy)
			except requests.exceptions.ConnectionError:
				self.logFile.write( u"Error: 連線失敗，請檢查網路連線狀態。"+'\r\n')
				self.logFile.write( "\tSkip "+URL['ltn']['root']+news+'\r\n')

			DOM = BeautifulSoup(r.text, 'html.parser')

			parseResult = {}

			parseResult['url'] = URL['ltn']['root']+news

			if len(re.findall('opinion', news, re.S)) > 0:

				##言論的page跟人加不一樣(；´Д｀)
				
				try:
					content = DOM.find('div', class_='content').find('div', class_='conbox')
				except TypeError:
					self.logFile.write( "TypeError: can't parse the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try:
					#Get title
					parseResult['title'] = content.h1.text
				except TypeError:
					self.logFile.write( "TypeError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				
				try:
					#Get date
					date = re.findall('([0-9]{4})-([0-9]{2})-([0-9]{2})', content.find('div', class_='writer').text, re.S)[0]
					parseResult['date'] = date[0]+date[1]+date[2]
				except TypeError:
					self.logFile.write( "TypeError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				
				try:
					#Get Time
					if len(re.findall('[0-9]{2}:[0-9]{2}', content.find('div', class_='writer').text, re.S)) > 0:
						parseResult['time'] = re.findall('[0-9]{2}:[0-9]{2}', content.find('div', class_='writer').text, re.S)[0]
					else:
						parseResult['time'] = ''
				except TypeError:
					self.logFile.write( "TypeError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				
				try:
					#Get newsText
					parseResult['newsText'] = ''
					for text in content.find('div', class_='cont').find_all('p'):
						parseResult['newsText'] = parseResult['newsText'] + text.text
				except TypeError:
					self.logFile.write( "TypeError: can't parse news Text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse news Text of  the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse news Text of  the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse news Text of  the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try:
					#GEt Aouthor
					parseResult['author'] = ''
					author = re.findall('〔(記者)?(.+)／', parseResult['newsText'].encode('utf-8'), re.S)[0][1]
					parseResult['author'] = author.decode('utf-8')
				except TypeError:
					self.logFile.write( "TypeError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue


				#Get type
				parseResult['type'] = u'言論'

			elif len(re.findall('entertainment', news, re.S)) > 0:
				##娛樂的page跟人加不一樣(；´Д｀)
				try:
					content = DOM.find('div', class_='news_content')
				except TypeError:
					self.logFile.write( "TypeError: can't parse the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try:
					#Get title
					parseResult['title'] = content.find('div', class_='Btitle').text
				except TypeError:
					self.logFile.write( "TypeError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try:
					#Get date
					date = re.findall('([0-9]{4})\/([0-9]{2})\/([0-9]{2})', content.find('div', class_='date').text, re.S)[0]
					parseResult['date'] = date[0]+date[1]+date[2]
				except TypeError:
					self.logFile.write( "TypeError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try:
					#Get time
					if len(re.findall('[0-9]{2}:[0-9]{2}', content.find('div', class_='date').text, re.S)) > 0:
						parseResult['time'] = re.findall('[0-9]{2}:[0-9]{2}', content.find('div', class_='date').text, re.S)[0]
					else:
						parseResult['time'] = ''
				except TypeError:
					self.logFile.write( "TypeError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try:
					#Get newsText
					parseResult['newsText'] = ''
					for text in content.find_all('p'):
						parseResult['newsText'] = parseResult['newsText'] + text.text
				except TypeError:
					self.logFile.write( "TypeError: can't parse news text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse news text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse news text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse news text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try:
					parseResult['author'] = ''
					author = re.findall('〔(記者)?(.+)／', parseResult['newsText'].encode('utf-8'), re.S)[0][1]
					parseResult['author'] = author.decode('utf-8')
				except TypeError:
					self.logFile.write( "TypeError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				#Get type
				parseResult['type'] = u'娛樂'

			else:
				try: 	
					#Get title
					parseResult['title'] = DOM.find('div', class_='content').h1.text
				except TypeError:
					self.logFile.write( "TypeError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse title of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

					
				try: 
					#Get date
					date = re.findall('([0-9]{4})[-]([0-9]{2})[-]([0-9]{2})', DOM.find('div', id='newstext').span.text, re.S)[0]
					parseResult['date'] = date[0]+date[1]+date[2]
				except TypeError:
					self.logFile.write( "TypeError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse date of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try: 					
					#Get time
					if len(re.findall('[0-9]{2}:[0-9]{2}', DOM.find('div', id='newstext').span.text, re.S)) > 0:
						parseResult['time'] = re.findall('[0-9]{2}:[0-9]{2}', DOM.find('div', id='newstext').span.text, re.S)[0]
					else:
						parseResult['time'] = ' '
				except TypeError:
					self.logFile.write( "TypeError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse time of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try: 
					#Get newsText
					parseResult['newsText'] = ''
					for text in DOM.find('div', id='newstext').find_all('p'):
						parseResult['newsText'] = parseResult['newsText'] + text.text
				except TypeError:
					self.logFile.write( "TypeError: can't parse news text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse news text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse news text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse news text of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

				try: 
					parseResult['author'] = ''
					author = re.findall('〔(記者)?(.+)／', parseResult['newsText'].encode('utf-8'), re.S)[0][1]
					parseResult['author'] = author.decode('utf-8')
				except TypeError:
					self.logFile.write( "TypeError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse author of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
					
				try: 
					#Get type 
					if len(re.findall('local', news, re.S)) > 0:
						parseResult['type'] = u'地方新聞'
					else:
						pag = DOM.find('div', class_='guide').find_all('a')
						parseResult['type'] = pag[len(pag)-1].text
				except TypeError:
					self.logFile.write( "TypeError: can't parse type of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except IndexError:
					self.logFile.write( "IndexError: can't parse type of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except AttributeError:
					self.logFile.write( "AttributeError: can't parse type of the news - "+URL['ltn']['root']+news+'\r\n')
					continue
				except KeyError:
					self.logFile.write( "KeyError: can't parse type of the news - "+URL['ltn']['root']+news+'\r\n')
					continue

			if self.soure == 'realtime':
				if len(lastData) == 0:
					lastData = parseResult
					self.logFile.write( 'the last news is in ' + lastData['date'])
			self.__writeToFile(parseResult)
				

	def __writeToFile(self, data):
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
		f = codecs.open(self.directory+'/'+data['date']+'_'+str(self.count)+'.txt', 'w', 
			'utf-8')
		f.write(u'\ufeff')
		fXml = codecs.open(self.directory+'/'+data['date']+'_'+str(self.count)+'.xml', 'w', 'utf-8')
		fXml.write(u'\ufeff')

		#過濾「記者」
		##data['author'] = data['author'].decode('utf-8').replace(u'\u8A18\u8005', '')

		f.write('Url:'+data['url']+'\r\n')
		f.write('Title:'+data['title']+'\r\n')
		f.write('clickNo:\r\n')
		f.write(u'Date:'+data['date']+'\r\n')
		f.write('Time:'+data['time']+'\r\n')
		f.write('Category:'+data['type']+'\r\n')
		f.write(u'Author:'+data['author']+'\r\n')
		f.write('Content:'+data['newsText']+'\r\n')
		f.close()

		## XML output
		fXml.write('<Article>\r\n')
		fXml.write('<Url>'+data['url']+'</url>\r\n')
		fXml.write('<ID>'+str(self.count)+'</ID>\r\n')
		fXml.write('<Category>'+data['type']+'</Category>\r\n')
		fXml.write('<Date>'+data['date']+'</Date>\r\n')
		fXml.write('<Time>'+data['time']+'</Time>\r\n')
		fXml.write('<Title>'+data['title']+'</Title>\r\n')
		fXml.write('<clickNo></clickNo>\r\n')
		fXml.write(u'<Authors>\r\n')
		for author in data['author'].split(u'、'):
			fXml.write(u'<Author>'+author+'</Author>\r\n')
		fXml.write('</Authors>\r\n')
		fXml.write('<Content>'+data['newsText']+'</Content>\r\n')
		fXml.write('</Article>')
		fXml.close()

		self.logListFile.write(self.directory+'/'+data['date']+'_'+str(self.count)+'.xml'+','+str(self.count)+','+data['title']+','+data['date']+','+data['type']+','+data['author']+'\r\n')
		self.ReportLog.write(data['author']+'\r\n')
		self.count = self.count + 1

	def execute(self):
		self.logFile.write( "Catch "+self.date+" from soure = "+self.soure+" of ltn"+'\r\n')
		#empty news list
		self.newsList = []
		self.__getList()
		self.__getContent()

class ListGetError:
	def __init__(self, arg):
		self.messages = arg

class ParseError:
	def __init__(self, arg):
		self.messages = arg
		
		

if len(sys.argv) > 2 and sys.argv[1] != 'ltn-realtime':
	startDay = datetime.date(int(sys.argv[2][0:4]), int(sys.argv[2][5:7]), int(sys.argv[2][8:10]))
	endDay = datetime.date(int(sys.argv[3][0:4]), int(sys.argv[3][5:7]), int(sys.argv[3][8:10]))

if sys.argv[1] == 'chinatimes':
	chinatime_spider = chinatimesSpider()
	currentDay = startDay
	while currentDay < endDay:
		print 'Cache chinatimes '+ str(currentDay)
		chinatime_spider.setDate(str(currentDay))
		for newstype in URL['chinatimes']['soure']:
			chinatime_spider.setSoure(newstype)
			chinatime_spider.setDir(newstype)
			chinatime_spider.execute()
		currentDay += datetime.timedelta(days=1)

if sys.argv[1] == 'ltn':
	s = ltnSpider()
	currentDay = startDay
	while currentDay < endDay:
		s.setDate(str(currentDay))
		for newstype in URL['ltn']['soure']:
			s.setSoure(newstype)
			s.setDir(newstype)
			s.execute()
		currentDay += datetime.timedelta(days=1)