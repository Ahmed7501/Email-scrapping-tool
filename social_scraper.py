"""
Social Media Scraper Module

This module handles scraping emails from social media platforms
like LinkedIn, Instagram, Facebook, and Twitter.
"""

import logging
import re
import time
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialScraper:
    """
    A class for scraping emails from social media platforms.
    
    This class provides methods to detect social media links
    and attempt to extract business emails from those platforms.
    """
    
    def __init__(self, scraper=None):
        """
        Initialize the SocialScraper.
        
        Args:
            scraper: WebScraper instance to use for making requests
        """
        self.scraper = scraper
        
        # Social media platform patterns
        self.social_patterns = {
            'linkedin': {
                'patterns': [
                    r'linkedin\.com/company/([^/\s]+)',
                    r'linkedin\.com/in/([^/\s]+)',
                    r'linkedin\.com/showcase/([^/\s]+)'
                ],
                'base_urls': [
                    'https://www.linkedin.com/company/',
                    'https://www.linkedin.com/in/',
                    'https://www.linkedin.com/showcase/'
                ]
            },
            'instagram': {
                'patterns': [
                    r'instagram\.com/([^/\s]+)',
                    r'instagr\.am/([^/\s]+)'
                ],
                'base_urls': [
                    'https://www.instagram.com/',
                    'https://instagr.am/'
                ]
            },
            'facebook': {
                'patterns': [
                    r'facebook\.com/([^/\s]+)',
                    r'fb\.com/([^/\s]+)'
                ],
                'base_urls': [
                    'https://www.facebook.com/',
                    'https://fb.com/'
                ]
            },
            'twitter': {
                'patterns': [
                    r'twitter\.com/([^/\s]+)',
                    r'x\.com/([^/\s]+)'
                ],
                'base_urls': [
                    'https://twitter.com/',
                    'https://x.com/'
                ]
            },
            'youtube': {
                'patterns': [
                    r'youtube\.com/channel/([^/\s]+)',
                    r'youtube\.com/c/([^/\s]+)',
                    r'youtube\.com/user/([^/\s]+)'
                ],
                'base_urls': [
                    'https://www.youtube.com/channel/',
                    'https://www.youtube.com/c/',
                    'https://www.youtube.com/user/'
                ]
            }
        }
        
        # Common social media link keywords
        self.social_keywords = {
            'linkedin', 'instagram', 'facebook', 'twitter', 'youtube',
            'linkedin.com', 'instagram.com', 'facebook.com', 'twitter.com',
            'x.com', 'youtube.com', 'fb.com', 'instagr.am'
        }
    
    def detect_social_links(self, links: List[str]) -> Dict[str, List[str]]:
        """
        Detect social media links from a list of URLs.
        
        Args:
            links (List[str]): List of URLs to analyze
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping platform names to lists of URLs
        """
        social_links = {platform: [] for platform in self.social_patterns.keys()}
        
        for link in links:
            link_lower = link.lower()
            
            for platform, config in self.social_patterns.items():
                for pattern in config['patterns']:
                    if re.search(pattern, link_lower):
                        social_links[platform].append(link)
                        break
        
        # Log findings
        total_social = sum(len(urls) for urls in social_links.values())
        if total_social > 0:
            logger.info(f"Detected {total_social} social media links")
            for platform, urls in social_links.items():
                if urls:
                    logger.info(f"  {platform}: {len(urls)} links")
        
        return social_links
    
    def scrape_social_emails(self, social_links: Dict[str, List[str]], 
                           max_per_platform: int = 3) -> List[Dict[str, Any]]:
        """
        Scrape emails from social media profiles.
        
        Args:
            social_links (Dict[str, List[str]]): Social media links by platform
            max_per_platform (int): Maximum number of profiles to scrape per platform
            
        Returns:
            List[Dict[str, Any]]: List of scraping results with emails found
        """
        results = []
        
        for platform, links in social_links.items():
            if not links:
                continue
            
            logger.info(f"Scraping emails from {platform} profiles...")
            
            # Limit the number of profiles per platform
            links_to_scrape = links[:max_per_platform]
            
            for link in links_to_scrape:
                try:
                    result = self._scrape_social_profile(platform, link)
                    if result:
                        results.append(result)
                    
                    # Add delay between requests
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error scraping {platform} profile {link}: {e}")
        
        return results
    
    def _scrape_social_profile(self, platform: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single social media profile.
        
        Args:
            platform (str): Social media platform name
            url (str): Profile URL
            
        Returns:
            Optional[Dict[str, Any]]: Scraping result or None if failed
        """
        if not self.scraper:
            logger.warning("No scraper instance provided, cannot scrape social profiles")
            return None
        
        try:
            # Scrape the profile page
            result = self.scraper.scrape_url(url)
            
            if result['status'] != 'success':
                return None
            
            # Extract emails from the content
            from email_extractor import EmailExtractor
            extractor = EmailExtractor()
            emails_with_context = extractor.extract_emails_from_html(
                result['html'], url
            )
            
            if emails_with_context:
                return {
                    'platform': platform,
                    'url': url,
                    'title': result.get('title', ''),
                    'emails': [email for email, context in emails_with_context],
                    'email_contexts': dict(emails_with_context),
                    'scraping_method': result.get('scraping_method', 'unknown'),
                    'status': 'success'
                }
            else:
                # Try to find contact information in the page
                contact_info = self._extract_contact_info(result['html'], platform)
                if contact_info:
                    return {
                        'platform': platform,
                        'url': url,
                        'title': result.get('title', ''),
                        'emails': [],
                        'contact_info': contact_info,
                        'scraping_method': result.get('scraping_method', 'unknown'),
                        'status': 'partial'
                    }
        
        except Exception as e:
            logger.error(f"Error scraping {platform} profile {url}: {e}")
        
        return None
    
    def _extract_contact_info(self, html: str, platform: str) -> Dict[str, Any]:
        """
        Extract contact information from social media profile HTML.
        
        Args:
            html (str): HTML content of the profile page
            platform (str): Social media platform name
            
        Returns:
            Dict[str, Any]: Extracted contact information
        """
        soup = BeautifulSoup(html, 'html.parser')
        contact_info = {}
        
        # Platform-specific extraction logic
        if platform == 'linkedin':
            contact_info = self._extract_linkedin_contact_info(soup)
        elif platform == 'instagram':
            contact_info = self._extract_instagram_contact_info(soup)
        elif platform == 'facebook':
            contact_info = self._extract_facebook_contact_info(soup)
        elif platform == 'twitter':
            contact_info = self._extract_twitter_contact_info(soup)
        
        return contact_info
    
    def _extract_linkedin_contact_info(self, soup) -> Dict[str, Any]:
        """Extract contact information from LinkedIn profile."""
        contact_info = {}
        
        try:
            # Look for contact information in various selectors
            contact_selectors = [
                '[data-control-name="contact_see_more"]',
                '.contact-info',
                '.contact-details',
                '[data-section="contact-info"]'
            ]
            
            for selector in contact_selectors:
                contact_element = soup.select_one(selector)
                if contact_element:
                    text = contact_element.get_text()
                    contact_info['raw_contact_text'] = text
                    break
            
            # Look for website links
            website_links = soup.find_all('a', href=True)
            websites = []
            for link in website_links:
                href = link.get('href', '')
                if href.startswith('http') and 'linkedin.com' not in href:
                    websites.append(href)
            
            if websites:
                contact_info['websites'] = websites
        
        except Exception as e:
            logger.debug(f"Error extracting LinkedIn contact info: {e}")
        
        return contact_info
    
    def _extract_instagram_contact_info(self, soup) -> Dict[str, Any]:
        """Extract contact information from Instagram profile."""
        contact_info = {}
        
        try:
            # Instagram often has contact info in bio or external links
            bio_selectors = [
                'meta[property="og:description"]',
                '.bio',
                '.profile-bio'
            ]
            
            for selector in bio_selectors:
                bio_element = soup.select_one(selector)
                if bio_element:
                    if bio_element.name == 'meta':
                        bio_text = bio_element.get('content', '')
                    else:
                        bio_text = bio_element.get_text()
                    
                    if bio_text:
                        contact_info['bio'] = bio_text
                        break
            
            # Look for external links in bio
            if 'bio' in contact_info:
                # Extract URLs from bio text
                url_pattern = r'https?://[^\s]+'
                urls = re.findall(url_pattern, contact_info['bio'])
                if urls:
                    contact_info['bio_urls'] = urls
        
        except Exception as e:
            logger.debug(f"Error extracting Instagram contact info: {e}")
        
        return contact_info
    
    def _extract_facebook_contact_info(self, soup) -> Dict[str, Any]:
        """Extract contact information from Facebook page."""
        contact_info = {}
        
        try:
            # Look for contact information in various places
            contact_selectors = [
                '[data-testid="contact_info"]',
                '.contact-info',
                '.page_contact_info'
            ]
            
            for selector in contact_selectors:
                contact_element = soup.select_one(selector)
                if contact_element:
                    text = contact_element.get_text()
                    contact_info['raw_contact_text'] = text
                    break
            
            # Look for website links
            website_links = soup.find_all('a', href=True)
            websites = []
            for link in website_links:
                href = link.get('href', '')
                if href.startswith('http') and 'facebook.com' not in href:
                    websites.append(href)
            
            if websites:
                contact_info['websites'] = websites
        
        except Exception as e:
            logger.debug(f"Error extracting Facebook contact info: {e}")
        
        return contact_info
    
    def _extract_twitter_contact_info(self, soup) -> Dict[str, Any]:
        """Extract contact information from Twitter profile."""
        contact_info = {}
        
        try:
            # Twitter bio information
            bio_selectors = [
                'meta[name="description"]',
                '.profile-bio',
                '[data-testid="UserDescription"]'
            ]
            
            for selector in bio_selectors:
                bio_element = soup.select_one(selector)
                if bio_element:
                    if bio_element.name == 'meta':
                        bio_text = bio_element.get('content', '')
                    else:
                        bio_text = bio_element.get_text()
                    
                    if bio_text:
                        contact_info['bio'] = bio_text
                        break
            
            # Look for website in profile
            website_selectors = [
                'a[data-testid="UserUrl"]',
                '.profile-website',
                'a[rel="me"]'
            ]
            
            for selector in website_selectors:
                website_element = soup.select_one(selector)
                if website_element:
                    href = website_element.get('href', '')
                    if href and href.startswith('http'):
                        contact_info['website'] = href
                        break
        
        except Exception as e:
            logger.debug(f"Error extracting Twitter contact info: {e}")
        
        return contact_info
    
    def follow_social_links(self, social_links: Dict[str, List[str]]) -> List[str]:
        """
        Follow social media links to find additional contact information.
        
        Args:
            social_links (Dict[str, List[str]]): Social media links by platform
            
        Returns:
            List[str]: Additional URLs found from social profiles
        """
        additional_urls = []
        
        for platform, links in social_links.items():
            for link in links[:2]:  # Limit to 2 links per platform
                try:
                    if self.scraper:
                        result = self.scraper.scrape_url(link)
                        if result['status'] == 'success':
                            # Extract links from the social profile
                            for profile_link in result.get('links', []):
                                if self._is_business_related(profile_link):
                                    additional_urls.append(profile_link)
                    
                    time.sleep(1)  # Be respectful
                    
                except Exception as e:
                    logger.error(f"Error following {platform} link {link}: {e}")
        
        return list(set(additional_urls))  # Remove duplicates
    
    def _is_business_related(self, url: str) -> bool:
        """
        Check if a URL is likely to be business-related.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if URL is business-related
        """
        business_keywords = {
            'contact', 'about', 'team', 'company', 'business',
            'services', 'products', 'careers', 'jobs', 'career'
        }
        
        url_lower = url.lower()
        
        # Check if URL contains business-related keywords
        for keyword in business_keywords:
            if keyword in url_lower:
                return True
        
        # Check if it's not a social media platform
        social_domains = {
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'tiktok.com', 'snapchat.com'
        }
        
        parsed_url = urlparse(url)
        if parsed_url.netloc in social_domains:
            return False
        
        return True


# Convenience function for quick social media detection
def detect_social_links(links: List[str]) -> Dict[str, List[str]]:
    """
    Convenience function to detect social media links.
    
    Args:
        links (List[str]): List of URLs to analyze
        
    Returns:
        Dict[str, List[str]]: Dictionary mapping platform names to lists of URLs
    """
    scraper = SocialScraper()
    return scraper.detect_social_links(links) 