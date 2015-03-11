import sys
import chinatimes
import ltn
import ltn_realtimes
import datetime

if len(sys.argv) > 2 and sys.argv[1] != 'ltn-realtime':
	startDay = datetime.date(int(sys.argv[2][0:4]), int(sys.argv[2][5:7]), int(sys.argv[2][8:10]))
	endDay = datetime.date(int(sys.argv[3][0:4]), int(sys.argv[3][5:7]), int(sys.argv[3][8:10]))

if sys.argv[1] == 'chinatimes':
	chinatime_spider = chinatimes.NewsSpider('chinatimes', 'chinatimes')
	currentDay = startDay
	while currentDay < endDay:
		print 'Cache chinatimes '+ str(currentDay)
		chinatime_spider.setDate(str(currentDay))
		chinatime_spider.execute()
		currentDay += datetime.timedelta(days=1)

if sys.argv[1] == 'ltn':
	s = ltn.NewsSpider('ltn')
	currentDay = startDay
	while currentDay < endDay:
		print 'Cache ltn '+ str(currentDay)
		s.setDate(str(currentDay))
		s.execute()
		currentDay += datetime.timedelta(days=1)

if sys.argv[1] == 'ltn-realtimes':
	ltn = ltn_realtimes.NewsSpider('ltn_realtimes')
	###currentDay = startDay
	###while currentDay < endDay:
	###print 'Cache ltn '+ str(currentDay)
		###ltn.setDate(str(currentDay))
	ltn.execute()
		###currentDay += datetime.timedelta(days=1)

if sys.argv[1] == 'ctee':
	ctee = chinatimes.NewsSpider('ctee', 'ctee')
	currentDay = startDay
	while currentDay < endDay:
		print 'Cache ctee '+ str(currentDay)
		ctee.setDate(str(currentDay))
		ctee.execute()
		currentDay += datetime.timedelta(days=1)

if sys.argv[1] == 'want':
	want = chinatimes.NewsSpider('want', 'want')
	currentDay = startDay
	while currentDay < endDay:
		print 'Cache want '+ str(currentDay)
		want.setDate(str(currentDay))
		want.execute()
		currentDay += datetime.timedelta(days=1)

if sys.argv[1] == 'chinatimes-realtime':
	realtime = chinatimes.NewsSpider('realtime', 'chinatimes-realtime')
	###currentDay = startDay
	print 'Cache chinatimes realtime '+ str(currentDay)
	###realtime.setDate(str(currentDay))
	realtime.execute()
	###currentDay += datetime.timedelta(days=1)

if sys.argv[1] == '--all':
	chinatime_spider = chinatimes.NewsSpider('chinatimes', 'chinatimes')
	s = ltn.NewsSpider('ltn')
	ltn_realtimes = ltn_realtimes.NewsSpider('ltn_realtimes')
	currentDay = startDay
	while currentDay < endDay:
		chinatime_spider.setDate(str(currentDay))
		print 'Cache chinatimes '+ str(currentDay)
		chinatime_spider.setSoure('chinatimes')
		chinatime_spider.setDirectory('chinatimes')
		chinatime_spider.execute()

		print 'Cache ctee '+ str(currentDay)
		chinatime_spider.setSoure('ctee')
		chinatime_spider.setDirectory('ctee')
		chinatime_spider.execute()

		print 'Cache want '+ str(currentDay)
		chinatime_spider.setSoure('want')
		chinatime_spider.setDirectory('wnat')
		chinatime_spider.execute()

		print 'Cache chinatimes realtime '+ str(currentDay)
		chinatime_spider.setSoure('realtime')
		chinatime_spider.setDirectory('chinatimes-realtime')
		chinatime_spider.execute()

		print 'Cache ltn '+ str(currentDay)
		s.setDate(str(currentDay))
		s.execute()
		currentDay += datetime.timedelta(days=1)

		print 'Cache ltn realtime '+ str(currentDay)
		ltn_realtimes.setDate(str(currentDay))
		ltn_realtimes.execute()
		currentDay += datetime.timedelta(days=1)