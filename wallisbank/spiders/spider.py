import scrapy

from scrapy.loader import ItemLoader

from ..items import WallisbankItem
from itemloaders.processors import TakeFirst
import requests

url = "https://www.wallisbank.com/news-events/"

payload={}
headers = {
  'authority': 'www.wallisbank.com',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'upgrade-insecure-requests': '1',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'same-origin',
  'sec-fetch-dest': 'empty',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8',
  'cookie': '_ga=GA1.2.2096533298.1616766024; _fbp=fb.1.1616766024014.1157772488; sucuri_cloudproxy_uuid_ea1b572d4=7ac294adb8c728e6810718de345b8d78; _gid=GA1.2.1056569803.1617010096'
}


class WallisbankSpider(scrapy.Spider):
	name = 'wallisbank'
	start_urls = ['https://www.wallisbank.com/news-events/']

	def parse(self, response):
		data = requests.request("GET", url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)

		post_links = raw_data.xpath('//a[@class="speedbump"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		title = response.xpath('//div[@class="col-sm-10 col-sm-offset-1 col-xs-12 "]/h1/text()').get()
		description = response.xpath('//section[@class="release-body container "]//div[@class="col-sm-10 col-sm-offset-1"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//p[@class="mb-no"]/text()').get()

		item = ItemLoader(item=WallisbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
