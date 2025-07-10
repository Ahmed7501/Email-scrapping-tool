"""
Main Email Scraper Module

This module orchestrates the complete email scraping workflow,
coordinating all other modules to scrape emails from URLs.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import our modules
from file_loader import load_urls
from selenium_scraper import SeleniumScraper
from email_extractor import extract_emails
from output_writer import save_results
from crawler import get_internal_pages
from proxy_manager import ProxyManager
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailScraper:
    """
    Main orchestrator class for email scraping.
    
    This class coordinates all the modules to perform complete
    email scraping from URLs extracted from various file formats.
    """
    
    def __init__(self, 
                 use_selenium: bool = True,
                 use_proxies: bool = False,
                 use_social_scraping: bool = True,
                 max_internal_pages: int = 5,
                 output_format: str = 'excel'):
        """
        Initialize the EmailScraper.
        
        Args:
            use_selenium (bool): Whether to use Selenium for dynamic content
            use_proxies (bool): Whether to use proxy rotation
            use_social_scraping (bool): Whether to scrape social media profiles
            max_internal_pages (int): Maximum number of internal pages to scrape
            output_format (str): Output format ('csv', 'excel', or 'both')
        """
        self.use_selenium = use_selenium
        self.use_proxies = use_proxies
        self.use_social_scraping = use_social_scraping
        self.max_internal_pages = max_internal_pages
        self.output_format = output_format
        
        # Initialize components
        self.file_parser = FileParser()
        self.email_extractor = EmailExtractor()
        self.output_writer = OutputWriter()
        
        # Initialize optional components
        self.scraper = None
        self.social_scraper = None
        self.proxy_handler = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all the scraping components."""
        try:
            # Initialize web scraper
            self.scraper = WebScraper(
                use_selenium=self.use_selenium,
                headless=True,
                timeout=30
            )
            
            # Initialize social scraper if enabled
            if self.use_social_scraping:
                self.social_scraper = SocialScraper(self.scraper)
            
            # Initialize proxy handler if enabled
            if self.use_proxies:
                self.proxy_handler = ProxyHandler(use_free_proxies=True)
                logger.info("Proxy rotation enabled")
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    def scrape_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scrape emails from URLs found in a file.
        
        Args:
            file_path (str): Path to the input file
            
        Returns:
            Dict[str, Any]: Complete scraping results and statistics
        """
        logger.info(f"Starting email scraping from file: {file_path}")
        
        try:
            # Step 1: Parse file and extract URLs
            logger.info("Step 1: Parsing file and extracting URLs...")
            urls = self.file_parser.parse_file(file_path)
            
            if not urls:
                logger.warning("No URLs found in the file")
                return self._create_empty_results()
            
            logger.info(f"Found {len(urls)} URLs to process")
            
            # Step 2: Scrape emails from URLs
            logger.info("Step 2: Scraping emails from URLs...")
            results = self._scrape_urls(urls)
            
            # Step 3: Process social media links if enabled
            if self.use_social_scraping and self.social_scraper:
                logger.info("Step 3: Processing social media links...")
                social_results = self._process_social_links(results)
                results.extend(social_results)
            
            # Step 4: Generate output files
            logger.info("Step 4: Generating output files...")
            output_files = self._generate_outputs(results)
            
            # Step 5: Create summary
            summary = self._create_summary(results, output_files)
            
            logger.info("Email scraping completed successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error during email scraping: {e}")
            raise
    
    def scrape_from_urls(self, urls: List[str]) -> Dict[str, Any]:
        """
        Scrape emails from a list of URLs (public method).
        Args:
            urls (List[str]): List of URLs to scrape
        Returns:
            Dict[str, Any]: Summary and output files
        """
        results = self._scrape_urls(urls)
        # Process social links if enabled
        if self.use_social_scraping:
            social_results = self._process_social_links(results)
            results.extend(social_results)
        # Generate output files
        output_files = self._generate_outputs(results)
        # Create summary
        summary = self._create_summary(results, output_files)
        return summary
    
    def _scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape emails from a list of URLs.
        
        Args:
            urls (List[str]): List of URLs to scrape
            
        Returns:
            List[Dict[str, Any]]: Scraping results
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}: {url}")
            
            try:
                # Scrape the main URL
                main_result = self._scrape_single_url(url)
                results.append(main_result)
                
                # If successful, scrape internal pages
                if main_result['status'] == 'success':
                    internal_results = self._scrape_internal_pages(url)
                    results.extend(internal_results)
                
                # Add delay between requests
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                results.append({
                    'url': url,
                    'status': 'failed',
                    'emails': [],
                    'error': str(e),
                    'source_type': 'main'
                })
        
        return results
    
    def _scrape_single_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single URL for emails.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Dict[str, Any]: Scraping result
        """
        try:
            if self.scraper is None:
                raise RuntimeError("WebScraper is not initialized.")
            # Scrape the page
            scrape_result = self.scraper.scrape_url(url)
            
            if scrape_result['status'] != 'success':
                return {
                    'url': url,
                    'status': 'failed',
                    'emails': [],
                    'error': scrape_result.get('error', 'Unknown error'),
                    'source_type': 'main'
                }
            
            # Extract emails from the content
            emails_with_context = self.email_extractor.extract_emails_from_html(
                scrape_result['html'], url
            )
            
            emails = [email for email, context in emails_with_context]
            
            return {
                'url': url,
                'status': 'success',
                'emails': emails,
                'source_page': url,
                'scraping_method': scrape_result.get('scraping_method', 'unknown'),
                'title': scrape_result.get('title', ''),
                'links': scrape_result.get('links', []),
                'source_type': 'main'
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'status': 'failed',
                'emails': [],
                'error': str(e),
                'source_type': 'main'
            }
    
    def _scrape_internal_pages(self, base_url: str) -> List[Dict[str, Any]]:
        """
        Scrape internal pages for additional emails.
        
        Args:
            base_url (str): Base URL to find internal pages from
            
        Returns:
            List[Dict[str, Any]]: Results from internal pages
        """
        results = []
        
        try:
            if self.scraper is None:
                return results
            # Get internal links
            internal_links = self.scraper.get_internal_links(
                base_url, max_depth=1
            )
            
            # Filter for relevant pages
            relevant_pages = self._filter_relevant_pages(internal_links)
            
            # Limit the number of pages to scrape
            pages_to_scrape = relevant_pages[:self.max_internal_pages]
            
            for page_url in pages_to_scrape:
                try:
                    result = self._scrape_single_url(page_url)
                    result['source_type'] = 'internal'
                    results.append(result)
                    
                    time.sleep(0.5)  # Shorter delay for internal pages
                    
                except Exception as e:
                    logger.error(f"Error scraping internal page {page_url}: {e}")
            
        except Exception as e:
            logger.error(f"Error getting internal pages for {base_url}: {e}")
        
        return results
    
    def _filter_relevant_pages(self, urls: List[str]) -> List[str]:
        """
        Filter URLs to find relevant pages for email extraction.
        
        Args:
            urls (List[str]): List of URLs to filter
            
        Returns:
            List[str]: Filtered list of relevant URLs
        """
        relevant_keywords = {
            'contact', 'about', 'team', 'company', 'business',
            'services', 'products', 'careers', 'jobs', 'career',
            'staff', 'people', 'leadership', 'management'
        }
        
        relevant_urls = []
        
        for url in urls:
            url_lower = url.lower()
            
            # Check if URL contains relevant keywords
            for keyword in relevant_keywords:
                if keyword in url_lower:
                    relevant_urls.append(url)
                    break
        
        return relevant_urls
    
    def _process_social_links(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process social media links found in scraping results.
        
        Args:
            results (List[Dict[str, Any]]): Previous scraping results
            
        Returns:
            List[Dict[str, Any]]: Social media scraping results
        """
        social_results = []
        
        if not self.social_scraper:
            return social_results

        # Collect all links from results
        all_links = []
        for result in results:
            links = result.get('links', [])
            all_links.extend(links)
        
        # Detect social media links
        social_links = self.social_scraper.detect_social_links(all_links)
        
        # Scrape social media profiles
        if any(social_links.values()):
            social_results = self.social_scraper.scrape_social_emails(social_links)
            
            # Convert to standard format
            for result in social_results:
                result['source_type'] = 'social'
        
        return social_results
    
    def _generate_outputs(self, results: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate output files in the specified format.
        
        Args:
            results (List[Dict[str, Any]]): Scraping results
            
        Returns:
            Dict[str, str]: Dictionary mapping output types to file paths
        """
        output_files = {}
        
        try:
            if self.output_format in ['csv', 'both']:
                csv_file = self.output_writer.write_results_to_csv(results)
                output_files['csv'] = csv_file
            
            if self.output_format in ['excel', 'both']:
                excel_file = self.output_writer.write_results_to_excel(results)
                output_files['excel'] = excel_file
            
            # Always generate detailed report
            report_file = self.output_writer.write_detailed_report(results)
            output_files['report'] = report_file
            
        except Exception as e:
            logger.error(f"Error generating outputs: {e}")
        
        return output_files
    
    def _create_summary(self, results: List[Dict[str, Any]], 
                       output_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a comprehensive summary of the scraping operation.
        
        Args:
            results (List[Dict[str, Any]]): Scraping results
            output_files (Dict[str, str]): Generated output files
            
        Returns:
            Dict[str, Any]: Complete summary
        """
        # Calculate statistics
        total_urls = len(results)
        successful_urls = len([r for r in results if r.get('status') == 'success'])
        failed_urls = len([r for r in results if r.get('status') == 'failed'])
        
        all_emails = []
        for result in results:
            emails = result.get('emails', [])
            all_emails.extend(emails)
        
        unique_emails = list(set(all_emails))
        
        # Count by source type
        source_counts = {}
        for result in results:
            source_type = result.get('source_type', 'unknown')
            source_counts[source_type] = source_counts.get(source_type, 0) + 1
        
        summary = {
            'total_urls_processed': total_urls,
            'successful_scrapes': successful_urls,
            'failed_scrapes': failed_urls,
            'success_rate': (successful_urls / total_urls * 100) if total_urls > 0 else 0,
            'total_emails_found': len(all_emails),
            'unique_emails_found': len(unique_emails),
            'emails_by_source': source_counts,
            'output_files': output_files,
            'timestamp': time.time(),
            'settings': {
                'use_selenium': self.use_selenium,
                'use_proxies': self.use_proxies,
                'use_social_scraping': self.use_social_scraping,
                'max_internal_pages': self.max_internal_pages,
                'output_format': self.output_format
            }
        }
        
        return summary
    
    def _create_empty_results(self) -> Dict[str, Any]:
        """Create empty results when no URLs are found."""
        return {
            'total_urls_processed': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'success_rate': 0,
            'total_emails_found': 0,
            'unique_emails_found': 0,
            'emails_by_source': {},
            'output_files': {},
            'timestamp': time.time(),
            'settings': {
                'use_selenium': self.use_selenium,
                'use_proxies': self.use_proxies,
                'use_social_scraping': self.use_social_scraping,
                'max_internal_pages': self.max_internal_pages,
                'output_format': self.output_format
            }
        }
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.scraper:
                self.scraper.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def main():
    """Main function to run the email scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email Scraper Tool')
    parser.add_argument('file_path', help='Path to the input file')
    parser.add_argument('--selenium', action='store_true', 
                       help='Use Selenium for dynamic content')
    parser.add_argument('--proxies', action='store_true',
                       help='Use proxy rotation')
    parser.add_argument('--no-social', action='store_true',
                       help='Disable social media scraping')
    parser.add_argument('--internal-pages', type=int, default=5,
                       help='Maximum internal pages to scrape')
    parser.add_argument('--output-format', choices=['csv', 'excel', 'both'],
                       default='excel', help='Output format')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.file_path).exists():
        print(f"Error: File {args.file_path} not found")
        return
    
    try:
        # Initialize and run scraper
        with EmailScraper(
            use_selenium=args.selenium,
            use_proxies=args.proxies,
            use_social_scraping=not args.no_social,
            max_internal_pages=args.internal_pages,
            output_format=args.output_format
        ) as scraper:
            
            results = scraper.scrape_from_file(args.file_path)
            
            # Print summary
            print("\n" + "="*50)
            print("EMAIL SCRAPING COMPLETED")
            print("="*50)
            print(f"Total URLs processed: {results['total_urls_processed']}")
            print(f"Successful scrapes: {results['successful_scrapes']}")
            print(f"Failed scrapes: {results['failed_scrapes']}")
            print(f"Success rate: {results['success_rate']:.2f}%")
            print(f"Total emails found: {results['total_emails_found']}")
            print(f"Unique emails found: {results['unique_emails_found']}")
            
            if results['output_files']:
                print("\nOutput files generated:")
                for output_type, file_path in results['output_files'].items():
                    print(f"  {output_type.upper()}: {file_path}")
            
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main() 