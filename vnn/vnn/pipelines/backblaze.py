import os
import json
import uuid
import requests
from itemadapter import ItemAdapter
from b2sdk.v1 import InMemoryAccountInfo, B2Api

class BackblazeB2Pipeline:
    def __init__(self, key_id, app_key, bucket_name):
        info = InMemoryAccountInfo()
        self.b2_api = B2Api(info)
        self.b2_api.authorize_account("production", key_id, app_key)
        self.bucket = self.b2_api.get_bucket_by_name(bucket_name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            key_id=crawler.settings.get('B2_KEY_ID'),
            app_key=crawler.settings.get('B2_APP_KEY'),
            bucket_name=crawler.settings.get('B2_BUCKET_NAME')
        )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ### Upload images ###
        image_urls = adapter.get('images_url') or []
        uploaded_images = []
        for url in image_urls:
            uploaded = self.upload_from_url(url, folder='images', spider=spider)
            if uploaded:
                uploaded_images.append(uploaded)
        adapter['images_url'] = uploaded_images

        ### Upload videos ###
        video_urls = adapter.get('videos_url') or []
        uploaded_videos = []
        for url in video_urls:
            uploaded = self.upload_from_url(url, folder='videos', spider=spider)
            if uploaded:
                uploaded_videos.append(uploaded)
        adapter['videos_url'] = uploaded_videos

        ### Upload JSON item ###
        filename = f"{uuid.uuid4()}.json"
        filepath = os.path.join("/tmp", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(adapter.asdict(), f, ensure_ascii=False, indent=2)
        self.bucket.upload_local_file(local_file=filepath, file_name=f"scrapy_data/{filename}")
        os.remove(filepath)
        spider.logger.info(f"[BackblazeB2Pipeline] Uploaded item as JSON: {filename}")

        return item

    def upload_from_url(self, url, folder='uploads', spider=None):
        try:
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()
            ext = os.path.splitext(url)[1] or ''
            filename = f"{folder}/{uuid.uuid4().hex}{ext}"
            self.bucket.upload_bytes(response.content, filename)
            if spider:
                spider.logger.info(f"[BackblazeB2Pipeline] Uploaded file: {filename}")
            return filename
        except Exception as e:
            if spider:
                spider.logger.warning(f"[BackblazeB2Pipeline] Failed to upload {url}: {e}")
            return None
