from itemadapter import ItemAdapter
from vnn.mysql_helper import MySQLHelper

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
        self.mysql_helper.insert_item(adapter.asdict())
        spider.logger.info(f"[VnnPipeline] Inserted item: {adapter.get('url')}")
        return item
