from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from vnn.mysql_helper import MySQLHelper
from vnn.pipelines.backblaze import BackblazeB2Pipeline

class VnnPipeline:
    def __init__(self, host, database, user, password):
        self.mysql_helper = MySQLHelper(host, database, user, password)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD')
        )

    def open_spider(self, spider):
        self.mysql_helper.connect()
        spider.logger.info("[VnnPipeline] Connected to MySQL")

    def close_spider(self, spider):
        self.mysql_helper.close()
        spider.logger.info("[VnnPipeline] Closed MySQL connection")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get('url')

        if not url:
            return item

        self.mysql_helper.insert_item(adapter.asdict())
        return item
