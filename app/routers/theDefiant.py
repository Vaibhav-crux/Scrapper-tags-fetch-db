from fastapi import APIRouter
from bs4 import BeautifulSoup
import aiohttp
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

async def fetch_title_and_author_and_content(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response_text = await response.text()
    soup = BeautifulSoup(response_text, 'html.parser')
    title = soup.find('h1', class_="font-heading font-semibold text-default text-[24px] leading-[32px] md:text-[40px] md:leading-[48px] mb-1")
    author = soup.find('a', class_="hover:text-primary-hover font-medium underline")
    content = soup.find('div', class_="prose font-heading marker:text-default prose-p:mb-2 prose-p:mt-0 prose-p:text-[#333] prose-p:text-base prose-a:text-[#0000FF] prose-ul:mb-2 prose-ul:mt-0 prose-li:m-0 prose-li:text-default prose-h2:text-[24px] prose-h2:font-bold prose-h2:leading-8 prose-h2:mt-6 prose-h2:mb-4 prose-h3:text-[20px] prose-h3:font-bold prose-h3:leading-8 prose-h4:text-[20px] prose-h4:font-bold prose-h4:leading-6 mt-7 mb-6")
    paragraphs = content.find_all('p')
    content_text = [p.text for p in paragraphs]
    return {"title": title.text if title else "Title not found", "author": author.text if author else "Author not found", "content": content_text}

@router.get("/theDefiantScrappedData")
async def fetch_sitemap_links():
    sitemap_url = "https://thedefiant.io/sitemap/post-sitemap.xml"
    async with aiohttp.ClientSession() as session:
        async with session.get(sitemap_url, headers=headers) as response:
            response_text = await response.text()
    soup = BeautifulSoup(response_text, 'lxml')
    urls = soup.find_all('url')
    formatted_day = datetime.now()

    # Get the current date
    current_date = datetime.now().date()
    # Calculate the date for one day before the current date
    one_day_before = current_date - timedelta(days=1)

    # Fetch and process articles in parallel
    tasks = []
    for url in urls:
        loc = url.find('loc').text
        lastmod = url.find('lastmod').text
        # Convert lastmod to a datetime object and get the date part
        lastmod_date = datetime.strptime(lastmod, '%Y-%m-%d').date()

        # Check if lastmod_date matches the current_date or one_day_before
        if lastmod_date == current_date or lastmod_date == one_day_before:
            tasks.append(fetch_title_and_author_and_content(loc))

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
