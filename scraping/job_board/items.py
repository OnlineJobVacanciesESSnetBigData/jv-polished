"""
This file defines, for each job board, the items (type of information) that would be scraped for each company
"""


import scrapy


class BaseItem(scrapy.Item):
    company_name = scrapy.Field()
    count = scrapy.Field()


class CareerjetItem(BaseItem):
    link_internal = scrapy.Field()