from fastapi import APIRouter
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import uuid
from datetime import datetime
import time

router = APIRouter()

async def fetch_article(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def scrape_article_async():
    url = "https://cointelegraph.com/tags/cryptocurrencies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html_content = await response.text()

    soup = BeautifulSoup(html_content, 'html.parser')
    articles = soup.find_all("p", class_="post-card-inline__text")
    article_links = soup.find_all("a", class_="post-card-inline__title-link")

    tasks = []
    async with aiohttp.ClientSession() as session:
        for article, link in zip(articles, article_links):
            article_text = article.text.strip()
            article_link = "https://cointelegraph.com" + link["href"]
            tasks.append(fetch_article(session, article_link, headers))

        responses = await asyncio.gather(*tasks)

    total_articles = len(articles)
    current_time = time.strftime("%H:%M:%S")
    current_date = datetime.now().strftime('%Y-%m-%d')

    print("totalArticlesExtracted", total_articles)
    print("currentDate", current_date)
    print("currentTime", current_time)

    return {"totalArticlesExtracted": total_articles, "currentDate": current_date, "currentTime": current_time}

@router.get("/coinTelegraphScrappedData")
async def scrape_article_handler():
    return await scrape_article_async()
