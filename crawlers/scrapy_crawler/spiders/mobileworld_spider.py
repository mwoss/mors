import os
import errno
from json import dumps
from re import compile
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from ..items import MobileWorldItem


class LinkedinSpider(CrawlSpider):
    regex = compile(r'^[^|]+')

    name = 'mobileworld_spider'
    allowed_domains = ['mobileworldcongress.com']
    start_urls = ['https://www.mobileworldcongress.com/exhibition/2018-exhibitors/']

    relative_path = 'mobileworld_data/'
    if not os.path.exists(os.path.dirname(relative_path)):
        try:
            os.makedirs(os.path.dirname(relative_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    rules = (
        Rule(LinkExtractor(
            allow=[
                'https://www\.mobileworldcongress\.com/exhibitor/.+',
                'https://www\.mobileworldcongress\.com/exhibition/2018-exhibitors/.+'
            ],
            deny=[
                # Here sites that scrapy_crawler shouldn't visit
            ]),
            callback='parse_item',
            follow=True),
    )

    def parse_item(self, response):
        item = MobileWorldItem()
        item.data['url'] = response.url
        item.data['title'] = response.xpath('//title/text()').extract_first()
        data = response.css('.api-description').xpath('./p/text()').extract()
        item.data['description'] = ''.join(data)
        if item.data['description'] and item.data['title']:
            file_name_match = self.regex.match(item.data['title'])
            file_name = file_name_match.group(0)
            with open(self.relative_path + file_name + '.json', 'w') as f:
                f.write(dumps(item.data, ensure_ascii=False))

