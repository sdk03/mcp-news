import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

def get_timeline_events(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Get key events timeline from Khaleej Times"""
    timeline_events = []
    
    # Find all timeline card boxes
    timeline_cards = soup.find_all('div', class_='card-box')
    
    for card in timeline_cards:
        try:
            # Get the title row
            title_row = card.find('div', class_='post-title-rows')
            if not title_row:
                continue
                
            # Get the timestamp
            time_stamp = title_row.find('div', class_='time-stmp')
            timestamp = ""
            if time_stamp:
                time_elem = time_stamp.find('span', class_='tme-evnt')
                date_elem = time_stamp.find('span', class_='date-evnt')
                if time_elem and date_elem:
                    timestamp = f"{time_elem.text.strip()} {date_elem.text.strip()}"
            
            # Get the headline
            headline_elem = title_row.find('h4')
            if not headline_elem:
                continue
                
            headline_link = headline_elem.find('a')
            if not headline_link:
                continue
                
            headline = headline_link.text.strip()
            event_id = headline_link.get('href', '').strip('#')
            
            timeline_events.append({
                'title': headline,
                'timestamp': timestamp,
                'event_id': event_id,
                'is_timeline': True
            })
            
        except Exception as e:
            logger.error(f"Error parsing timeline event: {str(e)}")
            continue
    
    return timeline_events

def get_card_articles(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Get articles formatted in card structure from Khaleej Times"""
    card_articles = []
    
    # Find all card articles
    card_elements = soup.find_all('li', class_='rcnt-evntPost')
    
    for card in card_elements:
        try:
            # Get the article content div
            content_div = card.find('div', class_='evnt-content')
            if not content_div:
                continue
                
            # Get the headline
            headline_elem = content_div.find('h2')
            if not headline_elem:
                continue
                
            headline = headline_elem.text.strip()
            
            # Get the content
            content_elem = content_div.find('div')
            content = ""
            if content_elem:
                paragraphs = content_elem.find_all('p')
                content = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])
            
            # Get the timestamp
            timestamp = ""
            time_elem = card.find('span', class_='tme-evnt')
            if time_elem:
                timestamp = time_elem.text.strip()
            
            card_articles.append({
                'title': headline,
                'content': content,
                'timestamp': timestamp,
                'is_card': True
            })
            
        except Exception as e:
            logger.error(f"Error parsing card article: {str(e)}")
            continue
    
    return card_articles

def get_headlines() -> List[Dict[str, str]]:
    """Get all main headlines from Khaleej Times, including the main top news, excluding the popular section, and including card articles and timeline events"""
    try:
        url = "https://www.khaleejtimes.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = []
        
        # Get the main top news first
        main_top_news = soup.find('div', class_='main-top-teaser-content')
        if main_top_news:
            main_headline = main_top_news.find('h1')
            if main_headline:
                headline_link = main_headline.find('a')
                if headline_link:
                    headline = {
                        'title': headline_link.get('title', '').strip(),
                        'url': headline_link.get('href', '').strip(),
                        'is_main': True
                    }
                    if headline['title'] and headline['url']:
                        headlines.append(headline)
            
            # Get the subtitle/description if available
            subtitle = main_top_news.find('p')
            if subtitle:
                subtitle_link = subtitle.find('a')
                if subtitle_link:
                    subtitle_text = subtitle_link.get_text().strip()
                    if subtitle_text:
                        headlines[0]['subtitle'] = subtitle_text
        
        # Find all article containers
        article_containers = soup.find_all('div', class_='rendered_board_article')
        
        for container in article_containers:
            # Skip if it's in the popular section
            if container.find_parent('div', class_='most-popuplar-ongoing-viral-outer'):
                continue
                
            # Find the headline link
            headline_link = container.find('a', title=True)
            if headline_link:
                headline = {
                    'title': headline_link.get('title', '').strip(),
                    'url': headline_link.get('href', '').strip(),
                    'is_main': False
                }
                if headline['title'] and headline['url']:
                    headlines.append(headline)
        
        # Get card articles
        card_articles = get_card_articles(soup)
        headlines.extend(card_articles)
        
        # Get timeline events
        timeline_events = get_timeline_events(soup)
        headlines.extend(timeline_events)
        
        return headlines
        
    except Exception as e:
        logger.error(f"Error fetching headlines from Khaleej Times: {str(e)}")
        return []

def get_headline() -> str:
    """Get the first main headline from Khaleej Times (for backward compatibility)"""
    headlines = get_headlines()
    if headlines:
        main_headline = headlines[0]
        if main_headline.get('subtitle'):
            return f"{main_headline['title']} - {main_headline['subtitle']}"
        return main_headline['title']
    return "No headlines found"

def get_article_content(url):
    """
    Fetch and parse the full article content from a given Khaleej Times URL.
    
    Args:
        url (str): The URL of the article to fetch
        
    Returns:
        dict: A dictionary containing:
            - title: Article title
            - content: List of paragraphs
            - author: Author name
            - date: Publication date
            - error: Error message if any
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get article title
        title = soup.find('h1', class_='article-title')
        title = title.text.strip() if title else "No title found"
        
        # Get article content
        content_div = soup.find('div', class_='article-center-wrap-nf')
        paragraphs = []
        
        if content_div:
            # Find all paragraph elements
            for p in content_div.find_all('p'):
                # Skip empty paragraphs and those with only whitespace
                text = p.text.strip()
                if text:
                    paragraphs.append(text)
        
        # Get author information
        author_div = soup.find('div', class_='details')
        author = None
        if author_div:
            author_name = author_div.find('h4')
            if author_name:
                author = author_name.text.strip()
        
        # Get publication date
        date = None
        date_element = soup.find('time')
        if date_element:
            date = date_element.text.strip()
        
        return {
            'title': title,
            'content': paragraphs,
            'author': author,
            'date': date,
            'error': None
        }
        
    except Exception as e:
        logger.error(f"Error fetching article content: {str(e)}")
        return {
            'title': None,
            'content': [],
            'author': None,
            'date': None,
            'error': str(e)
        } 