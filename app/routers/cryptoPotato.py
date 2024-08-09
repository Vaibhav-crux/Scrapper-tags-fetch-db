from fastapi import APIRouter
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import uuid
import asyncio
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

async def fetch_article_content(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response_text = await response.text()
    soup = BeautifulSoup(response_text, 'html.parser')
    title_div = soup.find('div', class_='page-title')
    title = title_div.find('h1').text.strip() if title_div else ""
    author_span = soup.find('span', class_='entry-user')
    author_link = author_span.find('a', class_='fn') if author_span else None
    author = author_link.text.strip() if author_link else ""
    content = soup.find('div', class_='coincodex-content')
    paragraphs = content.find_all('p') if content else []
    content_text = "\n".join([p.text for p in paragraphs])
    return {"title": title, "author": author, "content": content_text}

@router.get("/cryptoPotatoScrappedData")
async def get_articles():
    sitemap_url = 'https://cryptopotato.com/post-sitemap31.xml'
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    async with aiohttp.ClientSession() as session:
        async with session.get(sitemap_url, headers=headers) as response:
            response_text = await response.text()
    soup = BeautifulSoup(response_text, 'lxml')
    urls = soup.find_all('url')
    formatted_day = datetime.now()

    # Fetch and process articles in parallel
    tasks = []
    for url in urls:
        loc = url.find('loc').text
        date = url.find('lastmod').text
        date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        if formatted_date == today or formatted_date == yesterday:
            tasks.append(fetch_article_content(loc))

    # Wait for all tasks to complete
    for task in asyncio.as_completed(tasks):
        await task  # We don't need the result here, just wait for the task to complete

    total_articles = len(urls)  # Assuming all URLs are valid and should be processed
    current_time = time.strftime("%H:%M:%S")  # Get the current time in hh:mm:ss format
    current_date = datetime.now().strftime('%Y-%m-%d')

    print("totalArticlesExtracted", total_articles)
    print("currentDate", current_date)
    print("currentTime", current_time)

    return {"totalArticlesExtracted": total_articles, "currentDate": current_date, "currentTime": current_time}
