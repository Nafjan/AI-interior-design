import asyncio
import json
import os
import sys
import io
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv("../../.env")

class ScrapedProduct(BaseModel):
    name: str
    price_sar: float
    image_url: str
    product_url: str

async def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    llm_config = LLMConfig(provider="openrouter/google/gemini-2.5-flash", api_token=api_key)
    
    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=ScrapedProduct.schema(),
        extraction_type="schema",
        instruction="Extract a list of the first 5 sofas on the page. Include the name, price in SAR, main image URL, and full product URL.",
    )
    
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://www.alrugaibfurniture.com/ar/collections/sofas", config=run_config)
        print("Extraction Result:")
        print(result.extracted_content)

if __name__ == "__main__":
    asyncio.run(main())
