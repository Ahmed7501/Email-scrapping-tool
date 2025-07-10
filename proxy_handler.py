"""
Proxy Handler Module

This module handles proxy rotation and management for web scraping.
Provides functionality to use custom proxy lists or fetch free proxies.
"""

import logging
import random
import time
import requests
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import json
from bs4 import BeautifulSoup, Tag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProxyHandler:
    """
    A class for managing and rotating proxies for web scraping.
    
    This class provides methods to load custom proxy lists,
    fetch free proxies from various sources, and rotate through them.
    """
    
    def __init__(self, proxy_list: Optional[List[str]] = None, 
                 proxy_file: Optional[str] = None,
                 use_free_proxies: bool = False):
        """
        Initialize the ProxyHandler.
        
        Args:
            proxy_list (List[str]): List of proxy URLs in format 'http://ip:port'
            proxy_file (str): Path to file containing proxy list
            use_free_proxies (bool): Whether to fetch free proxies
        """
        self.proxies = []
        self.current_index = 0
        self.proxy_stats = {}  # Track proxy performance
        
        # Load proxies from different sources
        if proxy_list is not None:
            self.add_proxies(proxy_list)
        
        if proxy_file is not None:
            self.load_proxies_from_file(proxy_file)
        
        if use_free_proxies:
            self.fetch_free_proxies()
    
    def add_proxies(self, proxy_list: List[str]):
        """
        Add proxies to the handler.
        
        Args:
            proxy_list (List[str]): List of proxy URLs
        """
        for proxy in proxy_list:
            if self._validate_proxy_format(proxy):
                self.proxies.append(proxy)
                self.proxy_stats[proxy] = {
                    'success_count': 0,
                    'fail_count': 0,
                    'last_used': None,
                    'avg_response_time': 0
                }
        
        logger.info(f"Added {len(proxy_list)} proxies")
    
    def load_proxies_from_file(self, file_path: str):
        """
        Load proxies from a file.
        
        Args:
            file_path (str): Path to the proxy file
        """
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            proxy_list = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxy_list.append(line)
            
            self.add_proxies(proxy_list)
            logger.info(f"Loaded {len(proxy_list)} proxies from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading proxies from file {file_path}: {e}")
    
    def fetch_free_proxies(self, max_proxies: int = 50):
        """
        Fetch free proxies from various sources.
        
        Args:
            max_proxies (int): Maximum number of proxies to fetch
        """
        logger.info("Fetching free proxies...")
        
        # Multiple sources for free proxies
        sources = [
            self._fetch_from_proxylist_download,
            self._fetch_from_free_proxy_list,
            self._fetch_from_geonode
        ]
        
        for source_func in sources:
            try:
                proxies = source_func()
                if proxies:
                    self.add_proxies(proxies[:max_proxies])
                    if len(self.proxies) >= max_proxies:
                        break
            except Exception as e:
                logger.warning(f"Failed to fetch from {source_func.__name__}: {e}")
        
        logger.info(f"Fetched {len(self.proxies)} free proxies")
    
    def _fetch_from_proxylist_download(self) -> List[str]:
        """Fetch proxies from proxylist.download."""
        try:
            url = "https://www.proxy-list.download/api/v1/get?type=http"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            proxies = []
            for line in response.text.strip().split('\n'):
                if line:
                    proxies.append(f"http://{line}")
            
            return proxies
            
        except Exception as e:
            logger.error(f"Error fetching from proxylist.download: {e}")
            return []
    
    def _fetch_from_free_proxy_list(self) -> List[str]:
        """Fetch proxies from free-proxy-list.net."""
        try:
            url = "https://free-proxy-list.net/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            if not isinstance(soup, BeautifulSoup):
                soup = BeautifulSoup(str(soup), 'html.parser')
            proxies = []
            table = soup.find('table', class_='table')
            if table and isinstance(table, Tag):
                rows = table.find_all('tr')[1:]
                for row in rows:
                    if isinstance(row, Tag):
                        cols = row.find_all('td')
                        if len(cols) >= 8:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            https = cols[6].text.strip()
                            if https == 'yes':
                                proxies.append(f"https://{ip}:{port}")
            return proxies
        except Exception as e:
            logger.error(f"Error fetching from free-proxy-list.net: {e}")
            return []
    
    def _fetch_from_geonode(self) -> List[str]:
        """Fetch proxies from geonode.com."""
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            proxies = []
            
            for proxy in data.get('data', []):
                ip = proxy.get('ip')
                port = proxy.get('port')
                protocol = proxy.get('protocol', 'http')
                
                if ip and port:
                    proxies.append(f"{protocol}://{ip}:{port}")
            
            return proxies
            
        except Exception as e:
            logger.error(f"Error fetching from geonode: {e}")
            return []
    
    def get_next_proxy(self, strategy: str = 'round_robin') -> Optional[str]:
        """
        Get the next proxy based on the specified strategy.
        
        Args:
            strategy (str): Strategy to use ('round_robin', 'random', 'best_performance')
            
        Returns:
            Optional[str]: Next proxy URL or None if no proxies available
        """
        if not self.proxies:
            return None
        
        if strategy == 'round_robin':
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy
        
        elif strategy == 'random':
            return random.choice(self.proxies)
        
        elif strategy == 'best_performance':
            # Sort by success rate and response time
            sorted_proxies = sorted(
                self.proxies,
                key=lambda p: (
                    self.proxy_stats[p]['success_count'] - self.proxy_stats[p]['fail_count'],
                    -self.proxy_stats[p]['avg_response_time']
                ),
                reverse=True
            )
            return sorted_proxies[0] if sorted_proxies else None
        
        else:
            return self.proxies[0]
    
    def test_proxy(self, proxy: str, test_url: str = "http://httpbin.org/ip", timeout: int = 10) -> bool:
        """
        Test if a proxy is working.
        
        Args:
            proxy (str): Proxy URL to test
            test_url (str): URL to test against
            timeout (int): Timeout for the test
            
        Returns:
            bool: True if proxy is working, False otherwise
        """
        try:
            proxies = {'http': proxy, 'https': proxy}
            start_time = time.time()
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            response_time = time.time() - start_time
            if response.status_code == 200:
                self.proxy_stats[proxy]['success_count'] += 1
                self.proxy_stats[proxy]['last_used'] = time.time()
                current_avg = self.proxy_stats[proxy]['avg_response_time']
                success_count = self.proxy_stats[proxy]['success_count']
                self.proxy_stats[proxy]['avg_response_time'] = (
                    (current_avg * (success_count - 1) + response_time) / success_count
                )
                logger.debug(f"Proxy {proxy} test successful (response time: {response_time:.2f}s)")
                return True
            else:
                self.proxy_stats[proxy]['fail_count'] += 1
                return False
        except Exception as e:
            self.proxy_stats[proxy]['fail_count'] += 1
            logger.debug(f"Proxy {proxy} test failed: {e}")
            return False
    
    def test_all_proxies(self, test_url: str = "http://httpbin.org/ip") -> List[str]:
        """
        Test all proxies and return working ones.
        
        Args:
            test_url (str): URL to test against
            
        Returns:
            List[str]: List of working proxy URLs
        """
        working_proxies = []
        
        for proxy in self.proxies:
            if self.test_proxy(proxy, test_url):
                working_proxies.append(proxy)
        
        logger.info(f"Found {len(working_proxies)} working proxies out of {len(self.proxies)}")
        return working_proxies
    
    def remove_proxy(self, proxy: str):
        """Remove a proxy from the list."""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            if proxy in self.proxy_stats:
                del self.proxy_stats[proxy]
            logger.info(f"Removed proxy: {proxy}")
    
    def get_proxy_stats(self) -> Dict[str, Dict]:
        """Get statistics for all proxies."""
        return self.proxy_stats.copy()
    
    def _validate_proxy_format(self, proxy: str) -> bool:
        """Validate proxy URL format."""
        try:
            parsed = urlparse(proxy)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except Exception:
            return False
    
    def get_proxy_dict(self, proxy: str) -> Dict[str, str]:
        """
        Get proxy dictionary for requests library.
        
        Args:
            proxy (str): Proxy URL
            
        Returns:
            Dict[str, str]: Proxy dictionary for requests
        """
        return {
            'http': proxy,
            'https': proxy
        }


# Convenience function for quick proxy testing
def test_proxy(proxy: str) -> bool:
    """
    Convenience function to test a single proxy.
    
    Args:
        proxy (str): Proxy URL to test
        
    Returns:
        bool: True if proxy is working, False otherwise
    """
    handler = ProxyHandler()
    handler.add_proxies([proxy])
    return handler.test_proxy(proxy) 