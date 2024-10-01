import scrapy
from finance_news.items import FinanceNewsItem

class MoneytimesSpider(scrapy.Spider):
    source_name = "money_times"
    name = "moneytimes"
    allowed_domains = ["moneytimes.com.br"]
    start_urls = ["https://moneytimes.com.br/empresas",
                  "https://www.moneytimes.com.br/tag/comprar-ou-vender"]
    custom_settings = {
        "DOWNLOAD_DELAY": 2
    }

    #1. pegar urls
    #2. pra cada url navegar na pagina
    #3. dentro da pagina pegar o title, data e texto
    #4. salvar title, data da notícia, url, data de criação
    def parse(self, response):
        news_list = response.css(".news-item .news-item__content")
        for item in news_list:
            #url = item.xpath("h2").css("a").attrib["href"]
            url = item.css('h2 a ::attr(href)').get()
            yield response.follow(url, callback=self.parse_pagina_noticia)

        links_ul = response.css("ul.nav-links")
        next_page = links_ul.css("li:last-child a ::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_destaques(response):
        destaques = response.css(".news-list-destaques-card")
        for destaque in destaques:
            item = destaque.xpath("h2")
            anchor_noticia = item.css("a")
            title = anchor_noticia.css("::text").get()
            url_detalhe = anchor_noticia.attrib["href"]
            
    def parse_pagina_noticia(self, response):
        news_item = FinanceNewsItem()
        news_item["title"] = response.css(".single_title::text").get()
        news_item["date_created"] = response.css(".single_meta_author_infos_date_time::text").get()
        news_item["source_url"] = response.url
        news_item["source_name"] = self.source_name
        yield news_item
