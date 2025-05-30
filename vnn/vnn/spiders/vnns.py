import scrapy
import re
from parsel import Selector
from vnn.items import VnnItem
from scrapy_playwright.page import PageMethod
from bs4 import BeautifulSoup

class VnnsSpider(scrapy.Spider):
    name = "vnns"
    allowed_domains = ["vietnamnet.vn", "embed.vietnamnet.vn"]

    CATEGORY_MAP = {
        'thoi_su': 'https://vietnamnet.vn/thoi-su',
    }
    max_page = 0

    def start_requests(self):
        for category, url in self.CATEGORY_MAP.items():
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                cb_kwargs={'category': category}
            )
            for page in range(1, self.max_page + 1):
                paged_url = f"{url}-page{page}"
                yield scrapy.Request(
                    url=paged_url,
                    callback=self.parse,
                    cb_kwargs={'category': category}
                )

    def parse(self, response, category):
        for href in response.css('.title-bold a::attr(href)').getall():
            article_url = response.urljoin(href)
            yield scrapy.Request(
                url=article_url,
                callback=self.parse_article,
                errback=self.errback,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod('wait_for_selector', '.vnn-content-image img.lazy-loaded', timeout=20000),
                        PageMethod('wait_for_load_state', 'networkidle')
                    ],
                    category=category
                )
            )

    async def parse_article(self, response):
        item = VnnItem()

        self.extract_basic_fields(item, response)
        await self.extract_videos(item, response)
        self.extract_images(item, response)

        raw_html = response.css('#maincontent').get()
        item['html_content'] = self.process_html_content(raw_html, item['images_url'])

        yield item

        page = response.meta.get('playwright_page')
        if page:
            await page.close()

    def extract_basic_fields(self, item, response):
        item['category'] = response.meta.get('category')
        item['url'] = response.url
        item['title'] = response.css('.content-detail-title::text').get()
        item['author'] = response.css('.name a::text').getall()
        date = response.css('.bread-crumb-detail__time::text').getall()
        item['date'] = date[0].split()[2] if date else None
        item['lead'] = response.css('.sm-sapo-mb-0::text').get() or response.css('.content-detail-sapo::text').get()
        
        content = response.css('#maincontent p::text').getall()
        item['content'] = content or response.css('.maincontent p::text').getall()

    def extract_images(self, item, response):
        images_url = response.css('.vnn-content-image img.lazy-loaded::attr(data-original)').getall()
        item['images_url'] = images_url

    async def extract_videos(self, item, response):
        item['videos_url'] = await self.extract_videos_from_embed(response)


    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()

    async def extract_videos_from_embed(self, response):
        embed_src = response.css("iframe[src*='embed.vietnamnet.vn']::attr(src)").get()
        if not embed_src:
            return []

        embed_url = response.urljoin(embed_src)
        page = response.meta.get('playwright_page')
        if not page:
            return []

        context = page.context
        new_page = await context.new_page()
        try:
            await new_page.goto(embed_url, timeout=20000)
            await new_page.wait_for_load_state('networkidle')
            embed_html = await new_page.content()
            m3u8_urls = re.findall(r"https?://[^\s'\"\\]+?playlist\.m3u8(?:\?[^'\"]+)?", embed_html)
            return list(set(m3u8_urls)) if m3u8_urls else []
        finally:
            await new_page.close()


    def process_html_content(self, raw_html, images_url):
        if not raw_html:
            return ''

        soup = BeautifulSoup(raw_html, 'html.parser')
        imgs = soup.find_all('img')

        for i, img in enumerate(imgs):
            img_src = images_url[i] if i < len(images_url) else img.get('src', '')
            alt = img.get('alt', '')

            img.attrs = {}
            img['src'] = img_src
            if alt:
                img['alt'] = alt

        return str(soup)