from mcp.server.fastmcp import FastMCP

import logging
from news_sources.khaleej_times import get_headline, get_headlines, get_article_content


# Create an MCP server
mcp = FastMCP("News Scraper")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def get_khaleej_times() -> str:
    """Get the latest headline from Khaleej Times"""
    return get_headline()

@mcp.tool()
def get_khaleej_times_all() -> list:
    """Get all main headlines from Khaleej Times"""
    return get_headlines()

@mcp.tool()
def get_khaleej_times_article(url: str):
    """
    Get the full content of a Khaleej Times article from its URL.
    
    Args:
        url (str): The URL of the article to fetch
        
    Returns:
        dict: Article content including title, paragraphs, author, and date
    """
    return get_article_content(url)


if __name__ == "__main__":
    mcp.run() 