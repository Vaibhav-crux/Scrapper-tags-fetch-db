from fastapi import APIRouter
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import uuid
import time

router = APIRouter()

async def fetch_url(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def process_article(session, url, headers, today, yesterday):
    try:
        formatted_day = datetime.now()
        url_response = await fetch_url(session, url, headers)
        url_soup = BeautifulSoup(url_response, 'html.parser')
        breadcrumb = url_soup.find('div', class_='breadcrumb breadcrumbPag mt-lg-0 mt-3')
        author_span = url_soup.find('span', class_='auth-name')
        if breadcrumb and author_span:
            title = breadcrumb.find('span', class_='breadcrumb_last').text
            author_name = author_span.text.strip()
            paragraphs = url_soup.find_all('p')
            filtered_paragraphs = [p for p in paragraphs if not p.find_parent('div', class_='footer-tags-container')]
            content = ' '.join([p.get_text(strip=True) for p in filtered_paragraphs])
            content = re.sub(r'News Markets Cryptoguru Collection Contact Follow us on:', '', content, flags=re.IGNORECASE)
            content = re.sub(r'DAILY NEWSLETTER Your daily dose of Crypto news, Prices & other updates\.\.', '', content, flags=re.IGNORECASE)
            content = re.sub(r'TRENDING TODAY', '', content, flags=re.IGNORECASE)
            content = re.sub(r'Top News Cryptocurrency Prices Popular Coingape Academy Blogs Popular Categories Exclusive Contact Exclusive Contact Close', '', content, flags=re.IGNORECASE)
            content = re.sub(r'Exclusive Contact Close', '', content, flags=re.IGNORECASE)

            return str(uuid.uuid4())  # Return only the article ID
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return None

@router.get("/coinGapeScrappedData")
async def coin_gape_scrapped():
    sitemap_url = 'https://coingape.com/news-sitemap.xml'
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
    tasks = []

    async with aiohttp.ClientSession() as session:
        try:
            response = await fetch_url(session, sitemap_url, headers)
            soup = BeautifulSoup(response, 'lxml')
            urls = soup.find_all('url')

            for url in urls:
                loc = url.find('loc').text
                date = url.find('news:publication_date').text
                date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                if formatted_date == today or formatted_date == yesterday:
                    tasks.append(process_article(session, loc, headers, today, yesterday))

            articles = await asyncio.gather(*tasks)
            articles = [article for article in articles if article is not None]

        except Exception as e:
            print(f"Error fetching sitemap: {str(e)}")
            return {"error": "Failed to fetch sitemap"}

    total_articles = len(articles)
    current_time = time.strftime("%H:%M:%S")
    current_date = datetime.now().strftime('%Y-%m-%d')

    print("totalArticlesExtracted", total_articles)
    print("currentDate", current_date)
    print("currentTime", current_time)

    return {"totalArticlesExtracted": total_articles, "currentDate": current_date, "currentTime": current_time}
