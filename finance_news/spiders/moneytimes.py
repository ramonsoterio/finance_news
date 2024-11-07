from datetime import datetime

import scrapy
from scrapy.exceptions import CloseSpider
from soupsieve.util import lower

from finance_news.items import FinanceNewsItem

def is_valid_date(current_date, end_date):
    return current_date >= end_date

def format_date(raw_date):
    MONTH = 1
    divided_date = raw_date.split()
    available_months = {
        "jan": "Jan",
        "fev": "Feb",
        "mar": "Mar",
        "abr": "Apr",
        "mai": "May",
        "jun": "Jun",
        "jul": "Jul",
        "ago": "Aug",
        "set": "Sep",
        "out": "Oct",
        "nov": "Nov",
        "dez": "Dec",
    }
    english_month_name = available_months[divided_date[MONTH].lower()]
    divided_date[MONTH] = english_month_name
    cleaned_date = " ".join(divided_date)
    date_format = "%d %b %Y, %H:%M"
    new_date_obj = datetime.strptime(cleaned_date, date_format)
    return new_date_obj

class MoneytimesSpider(scrapy.Spider):
    source_name = "money_times"
    name = "moneytimes"
    allowed_domains = ["moneytimes.com.br"]
    start_urls = ["https://moneytimes.com.br/empresas"]
    custom_settings = {
        "DOWNLOAD_DELAY": 0.250
    }
    end_date = "2024-11-06"

    def parse(self, response):
        news_list = response.css(".news-item .news-item__content")
        for item in news_list:
            url = item.css('h2 a ::attr(href)').get()
            yield response.follow(url, callback=self.parse_pagina_noticia)

        links_ul = response.css("ul.nav-links")
        next_page = links_ul.css("li:last-child a ::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
            
    def parse_pagina_noticia(self, response):
        news_item = FinanceNewsItem()
        news_item["title"] = response.css(".single_title::text").get()
        raw_date = response.css(".single_meta_author_infos_date_time::text").get()
        formatted_date = format_date(raw_date)
        if not is_valid_date(formatted_date, datetime.strptime(self.end_date, "%Y-%m-%d")):
            raise CloseSpider("date_limit_reached")
        news_item["date_created"] = raw_date
        news_item["source_url"] = response.url
        news_item["source_name"] = self.source_name
        yield news_item
