#NewsSpider

##抓取報社
自由時報
中國時報 （旺報、工商時報、中國時報）

##執行方法
	python newsSpider.py 參數1 參數2 參數3
參數1可選 ltn 或 chinatimes
參數2 起點時間 格式YYYY-mm-dd
參數3 終點時間 格式YYYY-mm-dd

若不輸入參數3 只會有抓取 參數2 之日期資訊

新聞範圍抓取不包含終點時間該日
自由時報抓取時間點不可以包含程式執行當天（例如2015-05-30時，參數2不可以是2015-05-30，會無法抓取）

抓取即時新聞時，參數2和3會失效


##記者格式
中國時報採用DOM結構抓取，固定抓取article tag底下class為rp_name的div中的文字。

自由時報透過regular expression抓取〔開頭，／結尾的記者資料。
自由時報可於 parseAuthor 的function中增加記者的regular expression。
windows環境下在python 2對於編碼有敏感問題，請適度加上u'將條件轉為unicode
	
	conditions = [
		u'〔(記者)?(.+)／.+〕',
		u'〔(記者)?(.+)／'
	]

##錯誤處理
當抓取發生錯誤時都會寫入log檔，並將產生錯誤的URL紀錄於其中。


## Proxy 設定
原始碼53～56行處，可以修改proxy設定
	
	proxy = {
		"http": "http://proxy.hinet.net:80",
		"https": "https://proxy.hinet.net:80"
	}

##其他
- 報紙網站「結構」若改版，爬蟲程式會直接失效。
- 自由時報網站有可能再變動，程式無法保證之後改版能夠正確運作。
