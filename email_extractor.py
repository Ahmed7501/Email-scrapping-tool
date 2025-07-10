"""
Email Extractor Module

This module contains the core logic for extracting email addresses from HTML content
using regex patterns and filtering mechanisms.
"""

import re
import logging
from typing import List, Set, Tuple, Optional
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailExtractor:
    """
    A class for extracting email addresses from HTML content and URLs.
    
    This class provides methods to extract emails using regex patterns,
    filter out common false positives, and validate email addresses.
    """
    
    def __init__(self):
        """Initialize the EmailExtractor with regex patterns."""
        # Comprehensive email regex pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Common false positive patterns to filter out
        self.false_positive_patterns = [
            re.compile(r'example\.com$'),
            re.compile(r'test\.com$'),
            re.compile(r'domain\.com$'),
            re.compile(r'email\.com$'),
            re.compile(r'user@localhost'),
            re.compile(r'admin@localhost'),
            re.compile(r'root@localhost'),
        ]
        
        # Common email providers that are usually real
        self.trusted_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'protonmail.com', 'zoho.com'
        }
    
    def extract_emails_from_text(self, text: Optional[str], source_url: Optional[str] = None) -> List[str]:
        """
        Extract email addresses from plain text content.
        
        Args:
            text (str): The text content to search for emails
            source_url (str): The source URL for context (optional)
            
        Returns:
            List[str]: List of unique email addresses found
        """
        if not text:
            return []
        
        try:
            # Find all email matches
            matches = self.email_pattern.findall(text)
            
            # Debug: log all matches found
            if matches:
                logger.info(f"Found {len(matches)} potential email matches: {matches[:5]}...")
            
            # Filter and clean emails
            valid_emails = []
            for email in matches:
                email = email.lower().strip()
                if self._is_valid_email(email, source_url):
                    valid_emails.append(email)
            
            # Remove duplicates while preserving order
            unique_emails = list(dict.fromkeys(valid_emails))
            
            logger.info(f"Extracted {len(unique_emails)} unique emails from text")
            return unique_emails
            
        except Exception as e:
            logger.error(f"Error extracting emails from text: {e}")
            return []
    
    def extract_emails_from_html(self, html_content: Optional[str], base_url: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        Extract email addresses from HTML content with their source context.
        
        Args:
            html_content (str): The HTML content to search
            base_url (str): The base URL for resolving relative links
            
        Returns:
            List[Tuple[str, str]]: List of (email, source_context) tuples
        """
        if not html_content:
            return []
        
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            emails_with_context = []
            
            # Extract emails from text content
            text_emails = self.extract_emails_from_text(soup.get_text(), base_url)
            for email in text_emails:
                emails_with_context.append((email, "text_content"))
            
            # Extract emails from href attributes (mailto links)
            mailto_emails = self._extract_mailto_emails(soup, base_url)
            emails_with_context.extend(mailto_emails)
            
            # Extract emails from data attributes
            data_emails = self._extract_data_attribute_emails(soup, base_url)
            emails_with_context.extend(data_emails)
            
            # Remove duplicates while preserving order
            unique_emails = []
            seen_emails = set()
            for email, context in emails_with_context:
                if email not in seen_emails:
                    unique_emails.append((email, context))
                    seen_emails.add(email)
            
            logger.info(f"Extracted {len(unique_emails)} unique emails from HTML")
            return unique_emails
            
        except Exception as e:
            logger.error(f"Error extracting emails from HTML: {e}")
            return []
    
    def _extract_mailto_emails(self, soup, base_url: Optional[str]) -> List[Tuple[str, str]]:
        """Extract emails from mailto links."""
        emails = []
        try:
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0].strip()
                    if self._is_valid_email(email, base_url):
                        emails.append((email.lower(), "mailto_link"))
        except Exception as e:
            logger.error(f"Error extracting mailto emails: {e}")
        return emails
    
    def _extract_data_attribute_emails(self, soup, base_url: Optional[str]) -> List[Tuple[str, str]]:
        """Extract emails from data attributes."""
        emails = []
        try:
            for tag in soup.find_all(attrs=lambda x: x):
                for attr_name, attr_value in tag.attrs.items():
                    if isinstance(attr_value, str) and 'data-' in attr_name:
                        found_emails = self.extract_emails_from_text(attr_value, base_url)
                        for email in found_emails:
                            emails.append((email, f"data_attribute_{attr_name}"))
        except Exception as e:
            logger.error(f"Error extracting data attribute emails: {e}")
        return emails
    
    def _is_valid_email(self, email: str, source_url: Optional[str] = None) -> bool:
        """
        Validate if an email address is likely to be real.
        
        Args:
            email (str): The email address to validate
            source_url (str): The source URL for context
            
        Returns:
            bool: True if the email is likely valid, False otherwise
        """
        if not email or len(email) < 5:
            return False
        
        # Check for false positives
        for pattern in self.false_positive_patterns:
            if pattern.search(email):
                return False
        
        # Basic email format validation
        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
            return False
        
        # Extract domain
        domain = email.split('@')[1] if '@' in email else ''
        
        # If it's a trusted domain, it's more likely to be real
        if domain in self.trusted_domains:
            return True
        
        # If source URL is provided, check if domain matches
        if source_url:
            try:
                parsed_url = urlparse(source_url)
                url_domain = parsed_url.netloc.lower()
                if domain == url_domain or domain.endswith('.' + url_domain):
                    return True
            except Exception:
                pass
        
        # Be more permissive - accept most valid email formats
        # Only reject obvious false positives
        return True
        
        # Additional validation: check for common patterns
        if self._has_suspicious_patterns(email):
            return False
        
        return True
    
    def _has_suspicious_patterns(self, email: str) -> bool:
        """Check for suspicious patterns that indicate fake emails."""
        suspicious_patterns = [
            r'^[0-9]+@',  # Starts with numbers
            r'@[0-9]+\.[a-z]+$',  # Domain is mostly numbers
            r'^[a-z]{1,2}@',  # Very short local part
            r'@[a-z]{1,2}\.',  # Very short domain
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, email):
                return True
        
        return False
    
    def filter_emails_by_domain(self, emails: List[str], target_domains: Optional[Set[str]] = None) -> List[str]:
        """
        Filter emails to only include those from specific domains.
        
        Args:
            emails (List[str]): List of email addresses
            target_domains (Set[str]): Set of target domains to include
            
        Returns:
            List[str]: Filtered list of emails
        """
        if not target_domains:
            return emails
        
        filtered_emails = []
        for email in emails:
            domain = email.split('@')[1] if '@' in email else ''
            if domain in target_domains:
                filtered_emails.append(email)
        
        return filtered_emails


# Convenience function for quick email extraction
def extract_emails(html):
    # Robust regex for emails
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    return list(set(re.findall(email_regex, html))) 