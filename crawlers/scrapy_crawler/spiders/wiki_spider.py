import os
import errno
from json import dumps

from scrapy.linkextractor import LinkExtractor
from scrapy.spider import Rule, CrawlSpider
from ..utils.html_strip import remove_tags
from ..items import WikiItem


class WikiSpider(CrawlSpider):
    name = 'wiki_spider'
    allowed_domains = ['wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Main_Page']
    relative_path = 'data/'
    if not os.path.exists(os.path.dirname(relative_path)):
        try:
            os.makedirs(os.path.dirname(relative_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    rules = (
        Rule(LinkExtractor(allow="https://en\.wikipedia\.org/wiki/.+",
                           deny=[
                               "https://en\.wikipedia\.org/wiki/Wikipedia.*",
                               "https://en\.wikipedia\.org/wiki/Main_Page",
                               "https://en\.wikipedia\.org/wiki/Free_Content",
                               "https://en\.wikipedia\.org/wiki/Talk.*",
                               "https://en\.wikipedia\.org/wiki/Portal.*",
                               "https://en\.wikipedia\.org/wiki/Special.*",
                               "https://en\.wikipedia\.org/wiki/Special.*"
                           ]),
             callback='parse_item',
             follow=True),
    )

    def parse_item(self, response):
        title = response.css('head title::text').extract_first()
        content = response.xpath('//body/div[@id="content"]/div[@id="bodyContent"]').extract_first()
        item = WikiItem()
        item['title'] = title
        item['content'] = remove_tags(content)
        item['url'] = response.url
        file_name = item['url'].split('/')[-1]
        with open(self.relative_path + file_name + '.json', 'w', encoding='utf-8') as f:
            f.write(dumps(item.data, ensure_ascii=False))
