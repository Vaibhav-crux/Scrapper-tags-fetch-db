from fastapi import APIRouter
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import uuid
from datetime import datetime, timedelta
import time

router = APIRouter()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

async def fetch_page(session, url):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    section = soup.find('section', class_='at-body')
    content = "\n".join(p.text for p in section.find_all('p')) if section else ""
    author_div = soup.find('div', class_='at-authors')
    author_name = author_div.find('a').text if author_div and author_div.find('a') else ""
    return content, author_name

async def fetch_and_parse_article(session, url):
    html_content = await fetch_page(session, url)
    content, author_name = await parse_page(html_content)
    return str(uuid.uuid4())  # Return only the article ID

@router.get("/coinDeskScrappedData")
async def coin_desk_scrapped():
    sitemap_url = 'https://www.coindesk.com/arc/outboundfeeds/news-sitemap-index/?outputType=xml'
    async with aiohttp.ClientSession() as session:
        response = await session.get(sitemap_url, headers=headers)
        tasks = []

        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'lxml')
            url_tags = soup.find_all('url')
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            formatted_day = datetime.now()

            for url_tag in url_tags:
                # Check if the language is 'en'
                language_tag = url_tag.find('news:language')
                if language_tag and language_tag.text!= 'en':
                    continue  # Skip this iteration if the language is not 'en'

                loc_tag = url_tag.find('loc')
                date_tag = url_tag.find('lastmod')
                if date_tag:
                    date_only = date_tag.text.split('T')[0]
                    if date_only == today or date_only == yesterday:
                        tasks.append(fetch_and_parse_article(session, loc_tag.text))

            # Execute all tasks concurrently
            articles = await asyncio.gather(*tasks)

        else:
            print(f"Error: Received status code {response.status} when trying to fetch the sitemap.")
            return {"error": "Failed to fetch sitemap"}

    total_articles = len(articles)
    current_time = time.strftime("%H:%M:%S")  # Get the current time in hh:mm:ss format
    current_date = datetime.now().strftime('%Y-%m-%d')

    print("totalArticlesExtracted", total_articles)
    print("currentDate", current_date)
    print("currentTime", current_time)

    return {"totalArticlesExtracted": total_articles, "currentDate": current_date, "currentTime": current_time}
