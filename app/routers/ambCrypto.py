from fastapi import APIRouter
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import asyncio
import time

router = APIRouter()

@router.get("/ambcryptoScrappedData")
async def ambcrypto_scrapped():
    sitemap_url = 'https://ambcrypto.com/post-sitemap30.xml'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    articles = []

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(sitemap_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'lxml')
                url_tags = soup.find_all('url')
                today = datetime.now().strftime('%Y-%m-%d')

                async def fetch_article(url_tag):
                    lastmod_tag = url_tag.find('lastmod')
                    lastmod_text = lastmod_tag.text
                    date_obj = datetime.strptime(lastmod_text, "%Y-%m-%dT%H:%M:%S%z")
                    formatted_date = date_obj.strftime("%B %d, %Y")
                    if lastmod_tag and today in lastmod_tag.text:
                        return str(uuid.uuid4())  # Return the article ID
                    else:
                        return None

                tasks = [fetch_article(url_tag) for url_tag in url_tags]
                articles = await asyncio.gather(*tasks)
                
                articles = [article for article in articles if article is not None]
                
                total_articles = len(articles)
                current_time = time.strftime("%H:%M:%S")  # Get the current time in hh:mm:ss format
                current_date = datetime.now().strftime('%Y-%m-%d')

                print("totalArticlesExtracted", total_articles)
                print("currentDate", current_date)
                print("currentTime", current_time)

                return {"totalArticlesExtracted": total_articles, "currentDate": current_date, "currentTime": current_time}
            else:
                print(f"Error: Received status code {response.status} when trying to fetch the sitemap.")
                return {"error": f"Failed to fetch sitemap. Status code: {response.status}"}
