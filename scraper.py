"""
Web Scraper Module

This module handles web scraping using BeautifulSoup for static content
and Selenium for dynamic JavaScript-rendered content.
"""

import logging
import time
import requests
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """
    A class for scraping web pages using both BeautifulSoup and Selenium.
    
    This class provides methods to scrape static content with BeautifulSoup
    and dynamic content with Selenium WebDriver.
    """
    
    def __init__(self, use_selenium: bool = True, headless: bool = True, 
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialize the WebScraper.
        
        Args:
            use_selenium (bool): Whether to use Selenium for dynamic content
            headless (bool): Whether to run Selenium in headless mode
            timeout (int): Timeout for requests and Selenium operations
            max_retries (int): Maximum number of retries for failed requests
        """
        self.use_selenium = use_selenium
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Configure session headers
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Initialize Selenium driver if needed
        self.driver = None
        if self.use_selenium:
            self._init_selenium_driver()
    
    def _init_selenium_driver(self):
        """Initialize Selenium WebDriver with Chrome options."""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Additional options for better performance and stealth
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=' + self.ua.random)
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.use_selenium = False
    
    def scrape_url(self, url: str, use_selenium: bool = None) -> Dict[str, Any]:
        """
        Scrape a single URL and return the content and metadata.
        
        Args:
            url (str): The URL to scrape
            use_selenium (bool): Override default Selenium usage
            
        Returns:
            Dict[str, Any]: Scraping results with content, status, and metadata
        """
        if use_selenium is None:
            use_selenium = self.use_selenium
        
        result = {
            'url': url,
            'status': 'failed',
            'content': '',
            'html': '',
            'title': '',
            'links': [],
            'error': None,
            'scraping_method': 'requests' if not use_selenium else 'selenium'
        }
        
        try:
            if use_selenium and self.driver:
                result.update(self._scrape_with_selenium(url))
            else:
                result.update(self._scrape_with_requests(url))
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error scraping {url}: {e}")
        
        return result
    
    def _scrape_with_requests(self, url: str) -> Dict[str, Any]:
        """Scrape URL using requests and BeautifulSoup."""
        for attempt in range(self.max_retries):
            try:
                # Rotate user agent
                self.session.headers['User-Agent'] = self.ua.random
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Parse with BeautifulSoup
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ''
                
                # Extract links
                links = self._extract_links(soup, url)
                
                return {
                    'status': 'success',
                    'content': soup.get_text(),
                    'html': str(soup),
                    'title': title_text,
                    'links': links
                }
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Request failed for {url}, attempt {attempt + 1}: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _scrape_with_selenium(self, url: str) -> Dict[str, Any]:
        """Scrape URL using Selenium WebDriver."""
        try:
            # Navigate to URL
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source
            html = self.driver.page_source
            
            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            
            # Extract links
            links = self._extract_links(soup, url)
            
            return {
                'status': 'success',
                'content': soup.get_text(),
                'html': html,
                'title': title_text,
                'links': links
            }
            
        except TimeoutException:
            raise Exception("Page load timeout")
        except WebDriverException as e:
            raise Exception(f"Selenium error: {e}")
    
    def _extract_links(self, soup, base_url: str) -> List[str]:
        """Extract all links from the page."""
        links = []
        try:
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                if href:
                    # Resolve relative URLs
                    absolute_url = urljoin(base_url, href)
                    
                    # Only include HTTP/HTTPS links
                    if absolute_url.startswith(('http://', 'https://')):
                        links.append(absolute_url)
                        
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
        
        return list(set(links))  # Remove duplicates
    
    def scrape_multiple_urls(self, urls: List[str], 
                           use_selenium: bool = None) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs and return results.
        
        Args:
            urls (List[str]): List of URLs to scrape
            use_selenium (bool): Override default Selenium usage
            
        Returns:
            List[Dict[str, Any]]: List of scraping results
        """
        results = []
        
        for i, url in enumerate(urls):
            logger.info(f"Scraping URL {i+1}/{len(urls)}: {url}")
            
            result = self.scrape_url(url, use_selenium)
            results.append(result)
            
            # Add delay between requests to be respectful
            if i < len(urls) - 1:
                time.sleep(1)
        
        return results
    
    def get_internal_links(self, url: str, max_depth: int = 2) -> List[str]:
        """
        Get internal links from a website up to a certain depth.
        
        Args:
            url (str): The base URL to start from
            max_depth (int): Maximum depth to crawl
            
        Returns:
            List[str]: List of internal URLs found
        """
        base_domain = urlparse(url).netloc
        visited = set()
        to_visit = [(url, 0)]  # (url, depth)
        internal_links = []
        
        while to_visit:
            current_url, depth = to_visit.pop(0)
            
            if current_url in visited or depth > max_depth:
                continue
            
            visited.add(current_url)
            
            try:
                result = self.scrape_url(current_url)
                if result['status'] == 'success':
                    internal_links.append(current_url)
                    
                    # Add internal links to visit queue
                    if depth < max_depth:
                        for link in result['links']:
                            link_domain = urlparse(link).netloc
                            if link_domain == base_domain and link not in visited:
                                to_visit.append((link, depth + 1))
                                
            except Exception as e:
                logger.error(f"Error getting internal links from {current_url}: {e}")
        
        return internal_links
    
    def close(self):
        """Close the Selenium WebDriver and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing Selenium WebDriver: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function for quick scraping
def scrape_url(url: str, use_selenium: bool = True) -> Dict[str, Any]:
    """
    Convenience function to scrape a single URL.
    
    Args:
        url (str): The URL to scrape
        use_selenium (bool): Whether to use Selenium
        
    Returns:
        Dict[str, Any]: Scraping results
    """
    with WebScraper(use_selenium=use_selenium) as scraper:
        return scraper.scrape_url(url) 