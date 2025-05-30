import redis
from scrapy.exceptions import IgnoreRequest

class RedisDupeFilterMiddleware:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0, redis_key='scrapy:dupefilter'):
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        self.redis_key = redis_key

    @classmethod
    def from_crawler(cls, crawler):
        redis_host = crawler.settings.get('REDIS_HOST', 'localhost')
        redis_port = crawler.settings.get('REDIS_PORT', 6379)
        redis_db = crawler.settings.get('REDIS_DB', 0)
        redis_key = crawler.settings.get('REDIS_DUPEFILTER_KEY', 'scrapy:dupefilter')
        return cls(redis_host, redis_port, redis_db, redis_key)

    def process_request(self, request, spider):
        url = request.url
        if self.redis.sismember(self.redis_key, url):
            spider.logger.info(f"Duplicate URL (Redis): {url}")
            raise IgnoreRequest(f"Duplicate URL: {url}")
        else:
            self.redis.sadd(self.redis_key, url)
            return None
