BOT_NAME = "vnn"

SPIDER_MODULES = ["vnn.spiders"]
NEWSPIDER_MODULE = "vnn.spiders"

ROBOTSTXT_OBEY = False

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "data.json": {"format": "json", "overwrite": True},
    "data.csv": {"format": "csv", "overwrite": True},
}

DOWNLOAD_HANDLERS = {
    "http":  "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

ITEM_PIPELINES = {
    'vnn.pipelines.mysql_pipeline.VnnPipeline': 300,
    'vnn.pipelines.backblaze.BackblazeB2Pipeline': 200,
}

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Leduytung041a@'
MYSQL_DATABASE = 'vnn'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_DUPEFILTER_KEY = 'vnns:dupefilter'

B2_KEY_ID = '005cb05c4aaa2390000000003'
B2_APP_KEY = 'K0050WSsdZ9T54Z/wKQEIn5L3pZKgBI'
B2_BUCKET_NAME = 'testvnn'