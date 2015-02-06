import sys
import chinatimes
import ltn

if sys.argv[1] == 'chinatimes':
	chinatime_spider = chinatimes.NewsSpider('chinatimes', 'chinatimes')
	chinatime_spider.setDate(sys.argv[2])
	chinatime_spider.execute()

if sys.argv[1] == 'ltn':
	s = ltn.NewsSpider('ltn')
	s.setDate(sys.argv[2])
	s.execute()

if sys.argv[1] == '--all':
	chinatime_spider = chinatimes.NewsSpider('chinatimes', 'chinatimes')
	chinatime_spider.setDate(sys.argv[2])
	chinatime_spider.execute()
	s = ltn.NewsSpider('ltn')
	s.setDate(sys.argv[2])
	s.execute()