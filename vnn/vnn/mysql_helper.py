import mysql.connector
from mysql.connector import Error
import json
import datetime

class MySQLHelper:
    def __init__(self, host, database, user, password):
        self.conn = None
        self.cursor = None
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_table_if_not_exists(self):
        sql = """
        CREATE TABLE IF NOT EXISTS vnn_articles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(512) NOT NULL UNIQUE,
            category VARCHAR(255),
            title TEXT,
            `lead` TEXT,
            content LONGTEXT,
            html_content LONGTEXT,   -- thêm trường này
            date DATE,
            author TEXT,
            images_url TEXT,
            videos_url TEXT,
            crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def is_url_crawled(self, url):
        sql = "SELECT 1 FROM vnn_articles WHERE url = %s LIMIT 1"
        self.cursor.execute(sql, (url,))
        result = self.cursor.fetchone()
        return result is not None

    def get_all_crawled_urls(self):
        sql = "SELECT url FROM vnn_articles"
        self.cursor.execute(sql)
        return [row[0] for row in self.cursor.fetchall()]

    def insert_item(self, item):
        images_json = json.dumps(item.get('images_url') or [])
        videos_json = json.dumps(item.get('videos_url') or [])
        author_json = json.dumps(item.get('author') or [])

        content_val = item.get('content')
        if isinstance(content_val, list):
            content_val = '\n'.join(content_val).strip()
        elif content_val is None:
            content_val = ''

        html_content_val = item.get('html_content')
        if isinstance(html_content_val, list):
            html_content_val = '\n'.join(html_content_val).strip()
        elif html_content_val is None:
            html_content_val = ''

        lead_val = item.get('lead')
        if isinstance(lead_val, list):
            lead_val = '\n'.join(lead_val).strip()
        elif lead_val is None:
            lead_val = ''

        title_val = item.get('title')
        if isinstance(title_val, list):
            title_val = ' '.join(title_val).strip()
        elif title_val is None:
            title_val = ''

        date_val = item.get('date')
        if isinstance(date_val, str):
            try:
                date_val = datetime.datetime.strptime(date_val, '%d/%m/%Y').date()
            except Exception:
                date_val = None
        elif not isinstance(date_val, (datetime.date, type(None))):
            date_val = None

        sql = """
        INSERT INTO vnn_articles 
        (url, category, title, `lead`, content, html_content, date, author, images_url, videos_url) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        category = VALUES(category),
        title = VALUES(title),
        `lead` = VALUES(`lead`),
        content = VALUES(content),
        html_content = VALUES(html_content),
        date = VALUES(date),
        author = VALUES(author),
        images_url = VALUES(images_url),
        videos_url = VALUES(videos_url),
        crawl_time = CURRENT_TIMESTAMP
        """

        values = (
            item.get('url'),
            item.get('category'),
            title_val,
            lead_val,
            content_val,
            html_content_val,
            date_val,
            author_json,
            images_json,
            videos_json
        )
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
        except Error as e:
            print(f"MySQL insert error: {e}")
