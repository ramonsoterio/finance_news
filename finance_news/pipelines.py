# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from datetime import datetime
from soupsieve.util import lower
import re

class FinanceNewsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        raw_date = adapter.get("date_created")
        adapter["date_created"] = self.format_date(raw_date)
        adapter["title"] = self.format_title(adapter.get("title"))
        return item

    def format_date(self, raw_date):
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
        english_month_name = available_months[lower(divided_date[MONTH])]
        divided_date[MONTH] = english_month_name
        cleaned_date = " ".join(divided_date)
        date_format = "%d %b %Y, %H:%M"
        new_date_obj = datetime.strptime(cleaned_date, date_format)
        iso_format = new_date_obj.isoformat()
        return iso_format

    def format_title(self, title):
        cleaned = re.sub(r"[\t\n\r]", "", title)
        pattern = r"[\xA0\u2028\u2029]" #unicode
        cleaned = re.sub(pattern, " ", cleaned)
        return cleaned