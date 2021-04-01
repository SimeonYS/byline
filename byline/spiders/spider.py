import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BylineItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BylineSpider(scrapy.Spider):
	name = 'byline'
	page = 2
	start_urls = ['https://www.bylinebank.com/news/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news_list_item post_feed_column"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_url = f'https://www.bylinebank.com/news/?fwp_paged={self.page}#content'
		if post_links:
			self.page += 1
			yield response.follow(next_url, self.parse)


	def parse_post(self, response):
		date = response.xpath('//div[@class="date"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="content_column"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BylineItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
