# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WikiItem(scrapy.Item):
    # define the fields for your item here like:
    data = {
        'title': scrapy.Field(),
        'content': scrapy.Field(),
        'url': scrapy.Field()
    }


class GeneralItem(scrapy.Item):
    url = scrapy.Field()
    content = scrapy.Field()


class AdvanceGeneralItem(scrapy.Item):
    data = {
        'url': scrapy.Field(),
        'title': scrapy.Field(),
        'author': scrapy.Field(),
        'description': scrapy.Field(),
        'content': scrapy.Field()
    }


class LinkedinItem(scrapy.Item):
    data = {
        'url': scrapy.Field(),
        'title': scrapy.Field(),
        'description': scrapy.Field(),
    }


class MobileWorldItem(scrapy.Item):
    data = {
        'url': scrapy.Field(),
        'title': scrapy.Field(),
        'description': scrapy.Field(),
    }


class BBCItem(scrapy.Item):
    data = {
        'url': scrapy.Field(),
        'title': scrapy.Field(),
        'description': scrapy.Field(),
        'content': scrapy.Field()
    }
