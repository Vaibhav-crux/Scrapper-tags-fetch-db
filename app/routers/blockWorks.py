from fastapi import APIRouter
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import uuid
from datetime import datetime, timedelta
import time

router = APIRouter()

async def fetch_page(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    title_tag = soup.find('h1', class_="self-stretch flex-grow-0 flex-shrink-0 text-xl md:text-3xl lg:text-4xl xl:text-5xl font-headline text-left text-dark")
    author_div = soup.find('div', class_="flex flex-wrap gap-1 uppercase")
    div_section = soup.find('div', class_="p-2 basis-4/4 xl:basis-3/4")
    section = div_section.find('section', class_="w-full") if div_section else None
    paragraphs = section.find_all('p') if section else []
    content_text = ""
    for index, p in enumerate(paragraphs):
        if "Don’t miss the next big story" in p.text:
            if index == len(paragraphs) - 1:
                continue
        content_text += p.text + "\n"
    return title_tag.text if title_tag else "", author_div.find('a').text if author_div else "", content_text

async def fetch_and_parse_article(session, url):
    html_content = await fetch_page(session, url)
    title, author, content_text = await parse_page(html_content)
    return str(uuid.uuid4())  # Return only the article ID

@router.get("/blockWorksScrappedData")
async def block_works_scrapped():
    sitemap_url = 'https://blockworks.co/news-sitemap/1'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    async with aiohttp.ClientSession() as session:
        response = await session.get(sitemap_url, headers=headers)

        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'lxml')
            urls = soup.find_all('url')
            tasks = []
            for url in urls:
                loc = url.find('loc').text
                date_str = url.find('lastmod').text
                date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                
                if formatted_date == today or formatted_date == yesterday:
                    tasks.append(fetch_and_parse_article(session, loc))

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
