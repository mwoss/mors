import os
import errno

from goose3 import Goose
from json import dumps
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from ..items import AdvanceGeneralItem


class AdvanceGeneralSpider(CrawlSpider):
    file_id = 1
    goose = Goose({'enable_image_fetching': False})
    name = 'advance_general_spider'
    allowed_domains = ['reuters.com']

    start_urls = ['https://www.reuters.com/']

    relative_path = 'data/'
    if not os.path.exists(os.path.dirname(relative_path)):
        try:
            os.makedirs(os.path.dirname(relative_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    rules = (
        Rule(LinkExtractor(
            allow=[
                'https://www\.reuters\.com/.*'
            ],
            deny=[
                # Here sites that scrapy_crawler shouldn't visit
            ]),
            callback='parse_item',
            follow=True),
    )

    def parse_item(self, response):
        data = self.goose.extract(url=response.url)
        item = AdvanceGeneralItem()

        item.data['url'] = response.url
        item.data['title'] = data.title
        item.data['author'] = data.authors
        item.data['description'] = data.meta_description
        item.data['content'] = data.cleaned_text
        if item.data['content']:
            with open(self.relative_path + str(self.file_id) + '.json', 'w') as f:
                f.write(dumps(item.data, ensure_ascii=False))
                self.file_id += 1
