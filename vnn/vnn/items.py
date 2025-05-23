import scrapy

class VnnItem(scrapy.Item):
    url = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    lead = scrapy.Field()
    content = scrapy.Field()
    html_content = scrapy.Field()
    date = scrapy.Field()
    author = scrapy.Field()
    images_url = scrapy.Field()
    videos_url = scrapy.Field()
