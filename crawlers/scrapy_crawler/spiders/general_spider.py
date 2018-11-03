import os
import errno

from scrapy.linkextractor import LinkExtractor
from scrapy.spider import Rule, CrawlSpider
from ..utils.html_strip import clear_content_full
from ..items import GeneralItem


class GeneralSpider(CrawlSpider):
    name = 'general_spider'
    allowed_domains = ['iotdevfest.com',
                       'mobileworldcongress.com',
                       'tmt.knect365.com']

    start_urls = ['https://tmt.knect365.com/iot-world/',
                  'https://www.mobileworldcongress.com',
                  'https://www.iotdevfest.com/',
                  'https://www.embedded-world.de/en']

    relative_path = 'data/'
    if not os.path.exists(os.path.dirname(relative_path)):
        try:
            os.makedirs(os.path.dirname(relative_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    rules = (
        Rule(LinkExtractor(allow=['https://tmt\.knect365\.com/.+',
                                  'https://www\.mobileworldcongress\.com/.+',
                                  'https://www\.iotdevfest\.com/.+',
                                  'http://singapore.azurebootcamp\.net/.+',
                                  'https://www\.embedded-world\.de/en/.+'],
                           deny=[
                               # Here sites that scrapy_crawler shouldn't visit
                           ]),
             callback='parse_item',
             follow=True),
    )

    def parse_item(self, response):
        content = response.xpath('//body').extract_first()
        item = GeneralItem()
        item['content'] = clear_content_full(content)
        item['url'] = response.url
        file_name = item['url'].split('/')[-1]
        with open(self.relative_path + file_name + '.txt', 'w') as f:
            f.write(item['content'])
