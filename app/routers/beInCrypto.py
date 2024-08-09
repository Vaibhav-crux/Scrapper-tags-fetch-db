import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import uuid
from fastapi import APIRouter
import time

router = APIRouter()

@router.get("/beinCryptoScrappedData")
async def get_articles():
    base_sitemap_url = 'https://beincrypto.com/wp-content/uploads/beincrypto-sitemaps/sitemap_index/news/sitemap.xml'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    today = datetime.now().strftime('%Y-%m-%d')
    previous_day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    sitemap_url = base_sitemap_url

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(sitemap_url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'lxml')
                urls = soup.find_all('url')
                
                async def fetch_article(url):
                    loc = url.find('loc').text
                    day = url.find('news:publication_date').text.split('T')[0]
                    date_obj = datetime.strptime(day, '%Y-%m-%d')
                    
                    if day == today or day == previous_day:
                        return str(uuid.uuid4())  # Return the article ID
                    else:
                        return None
                
                tasks = [fetch_article(url) for url in urls]
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
