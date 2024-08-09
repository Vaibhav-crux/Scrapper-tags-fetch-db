from fastapi import APIRouter, Depends
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
import aiohttp
import uuid

router = APIRouter()

async def fetch_article_content(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_author_name_and_content(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    author_tag = soup.find('a', class_='contrib-link--name remove-underline author-name--tracking not-premium-contrib-link--name')
    article_div = soup.find('div', class_='article-body fs-article fs-responsive-text current-article')
    if article_div:
        paragraphs = article_div.find_all('p')
        paragraph_content = " ".join([p.get_text() for p in paragraphs])
    else:
        paragraph_content = "Article content not found."

    return author_tag.text if author_tag else "Unknown Author", paragraph_content

@router.get("/forbesScrappedData")
async def forbes_scrapped():
    sitemap_url = 'https://www.forbes.com/news_sitemap.xml'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    response = requests.get(sitemap_url, headers=headers)

    formatted_day = datetime.now()

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        url_tags = soup.find_all('url')
        current_date = datetime.now().strftime('%Y-%m-%d')
        total_articles = len(url_tags)  # Total number of articles based on the sitemap

        return {"totalArticlesExtracted": total_articles, "currentDate": current_date, "currentTime": formatted_day.strftime('%H:%M:%S')}
    else:
        print(f"Error: Received status code {response.status_code} when trying to fetch the sitemap.")
        return {"error": "Failed to fetch sitemap"}
