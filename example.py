"""
Example script demonstrating how to use the Email Scraper Tool.

This script shows various ways to use the tool programmatically.
"""

import logging
from main import EmailScraper
from file_parser import FileParser
from email_extractor import EmailExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example of basic usage with default settings."""
    print("=== Basic Usage Example ===")
    
    # Create a simple test file with URLs
    test_urls = [
        "https://httpbin.org",
        "https://www.example.com",
        "https://www.google.com"
    ]
    
    with open('example_urls.txt', 'w') as f:
        for url in test_urls:
            f.write(url + '\n')
    
    # Initialize and run scraper
    with EmailScraper(
        use_selenium=False,  # Use requests only for faster demo
        use_proxies=False,
        use_social_scraping=False,
        max_internal_pages=2,
        output_format='excel'
    ) as scraper:
        
        results = scraper.scrape_from_file('example_urls.txt')
        
        print(f"Processed {results['total_urls_processed']} URLs")
        print(f"Found {results['unique_emails_found']} unique emails")
        print(f"Success rate: {results['success_rate']:.2f}%")
        
        if results['output_files']:
            print("\nOutput files generated:")
            for output_type, file_path in results['output_files'].items():
                print(f"  {output_type}: {file_path}")


def example_advanced_usage():
    """Example of advanced usage with all features enabled."""
    print("\n=== Advanced Usage Example ===")
    
    # Create a test file with business URLs
    business_urls = [
        "https://www.linkedin.com/company/microsoft",
        "https://www.github.com",
        "https://www.stackoverflow.com"
    ]
    
    with open('business_urls.txt', 'w') as f:
        for url in business_urls:
            f.write(url + '\n')
    
    # Initialize scraper with all features
    with EmailScraper(
        use_selenium=True,
        use_proxies=True,
        use_social_scraping=True,
        max_internal_pages=3,
        output_format='both'
    ) as scraper:
        
        results = scraper.scrape_from_file('business_urls.txt')
        
        print(f"Advanced scraping completed:")
        print(f"  URLs processed: {results['total_urls_processed']}")
        print(f"  Successful scrapes: {results['successful_scrapes']}")
        print(f"  Failed scrapes: {results['failed_scrapes']}")
        print(f"  Total emails found: {results['total_emails_found']}")
        print(f"  Unique emails: {results['unique_emails_found']}")
        print(f"  Success rate: {results['success_rate']:.2f}%")
        
        # Show emails by source
        if results['emails_by_source']:
            print("\nEmails by source:")
            for source, count in results['emails_by_source'].items():
                print(f"  {source}: {count}")


def example_individual_components():
    """Example of using individual components."""
    print("\n=== Individual Components Example ===")
    
    # Example 1: File parsing
    print("1. File Parsing:")
    parser = FileParser()
    
    # Create a CSV file
    csv_content = """url,company
https://example.com,Example Corp
https://test.com,Test Inc
"""
    with open('example.csv', 'w') as f:
        f.write(csv_content)
    
    urls = parser.parse_file('example.csv')
    print(f"   Parsed {len(urls)} URLs from CSV")
    
    # Example 2: Email extraction
    print("2. Email Extraction:")
    extractor = EmailExtractor()
    
    sample_text = """
    Contact us at:
    - support@example.com
    - sales@example.com
    - info@test.com
    """
    
    emails = extractor.extract_emails_from_text(sample_text)
    print(f"   Extracted {len(emails)} emails from text")
    for email in emails:
        print(f"     - {email}")
    
    # Example 3: HTML email extraction
    print("3. HTML Email Extraction:")
    html_content = """
    <html>
        <body>
            <p>Contact: <a href="mailto:contact@example.com">contact@example.com</a></p>
            <p>Support: support@example.com</p>
            <div data-email="info@example.com">Info</div>
        </body>
    </html>
    """
    
    emails_with_context = extractor.extract_emails_from_html(html_content)
    print(f"   Extracted {len(emails_with_context)} emails from HTML")
    for email, context in emails_with_context:
        print(f"     - {email} (from {context})")


def example_custom_configuration():
    """Example of custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Create a test file
    with open('custom_test.txt', 'w') as f:
        f.write("https://httpbin.org\n")
    
    # Custom configuration
    config = {
        'use_selenium': False,  # Use requests only
        'use_proxies': False,   # No proxies
        'use_social_scraping': False,  # No social media
        'max_internal_pages': 1,  # Minimal internal pages
        'output_format': 'csv'  # CSV output only
    }
    
    print(f"Using configuration: {config}")
    
    with EmailScraper(**config) as scraper:
        results = scraper.scrape_from_file('custom_test.txt')
        
        print(f"Results: {results['unique_emails_found']} unique emails found")
        print(f"Output files: {list(results['output_files'].keys())}")


def main():
    """Run all examples."""
    print("Email Scraper Tool - Examples")
    print("=" * 40)
    
    try:
        # Run examples
        example_basic_usage()
        example_individual_components()
        example_custom_configuration()
        
        # Advanced example (commented out to avoid long execution)
        # example_advanced_usage()
        
        print("\n" + "=" * 40)
        print("Examples completed successfully!")
        print("Check the 'output' directory for generated files.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        logger.error(f"Example error: {e}")


if __name__ == "__main__":
    main() 