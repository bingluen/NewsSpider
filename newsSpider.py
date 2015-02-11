import sys
import chinatimes
import ltn
import datetime

startDay = datetime.date(int(sys.argv[2][0:4]), int(sys.argv[2][5:7]), int(sys.argv[2][8:10]))
endDay = datetime.date(int(sys.argv[3][0:4]), int(sys.argv[3][5:7]), int(sys.argv[3][8:10]))

if sys.argv[1] == 'chinatimes':
	chinatime_spider = chinatimes.NewsSpider('chinatimes', 'chinatimes')
	currentDay = startDay
	while currentDay < endDay:
		chinatime_spider.setDate(str(currentDay))
		chinatime_spider.execute()
		currentDay += datetime.timedelta(days=1)

if sys.argv[1] == 'ltn':
	s = ltn.NewsSpider('ltn')
	currentDay = startDay
	while currentDay < endDay:
		s.setDate(str(currentDay))
		s.execute()
		currentDay += datetime.timedelta(days=1)

if sys.argv[1] == '--all':
	chinatime_spider = chinatimes.NewsSpider('chinatimes', 'chinatimes')
	s = ltn.NewsSpider('ltn')
	currentDay = startDay
	while currentDay < endDay:
		chinatime_spider.setDate(str(currentDay))
		chinatime_spider.execute()
		s.setDate(str(currentDay))
		s.execute()
		currentDay += datetime.timedelta(days=1)