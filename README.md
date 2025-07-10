# Email Scraper Tool

A comprehensive, modular Python tool for scraping email addresses from websites. This tool can extract emails from various file formats, scrape websites using both BeautifulSoup and Selenium, and even extract emails from social media profiles.

## 🚀 Features

### Core Functionality
- **Multi-format File Support**: Parse URLs from CSV, Excel (.xlsx, .xls), TXT, and DOCX files
- **Advanced Web Scraping**: Uses both BeautifulSoup (static content) and Selenium (dynamic JavaScript content)
- **Email Extraction**: Sophisticated regex-based email extraction with filtering and validation
- **Internal Page Crawling**: Automatically discovers and scrapes relevant internal pages (Contact, About, Team, etc.)
- **Social Media Integration**: Detects and scrapes emails from LinkedIn, Instagram, Facebook, Twitter, and YouTube profiles

### Advanced Features
- **Proxy Rotation**: Built-in proxy management with free proxy fetching and rotation
- **User-Agent Rotation**: Automatic user-agent rotation to avoid detection
- **Comprehensive Output**: Export results to CSV, Excel (with multiple sheets), and detailed reports
- **Error Handling**: Robust error handling with retry mechanisms
- **Logging**: Detailed logging for debugging and monitoring

## 📁 Project Structure

```
email-scrapper-tool/
├── email_extractor.py      # Core email extraction logic
├── file_parser.py          # File parsing for various formats
├── scraper.py              # Web scraping with BeautifulSoup/Selenium
├── social_scraper.py       # Social media scraping
├── proxy_handler.py        # Proxy rotation and management
├── output_writer.py        # Output generation (CSV/Excel)
├── main.py                 # Main orchestrator
├── requirements.txt        # Python dependencies
├── test_urls.txt          # Sample URLs for testing
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- Chrome browser (for Selenium)

### Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd email-scrapper-tool
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Chrome WebDriver** (for Selenium)
   - Download ChromeDriver from: https://chromedriver.chromium.org/
   - Add it to your system PATH or place it in the project directory

## 📖 Usage

### Command Line Interface

The tool can be used from the command line with various options:

```bash
# Basic usage
python main.py input_file.txt

# With Selenium for dynamic content
python main.py input_file.txt --selenium

# With proxy rotation
python main.py input_file.txt --proxies

# Disable social media scraping
python main.py input_file.txt --no-social

# Limit internal pages
python main.py input_file.txt --internal-pages 3

# Output format
python main.py input_file.txt --output-format csv
```

### Python API

You can also use the tool programmatically:

```python
from main import EmailScraper

# Initialize the scraper
with EmailScraper(
    use_selenium=True,
    use_proxies=False,
    use_social_scraping=True,
    max_internal_pages=5,
    output_format='excel'
) as scraper:
    
    # Scrape emails from a file
    results = scraper.scrape_from_file('urls.txt')
    
    # Print summary
    print(f"Found {results['unique_emails_found']} unique emails")
    print(f"Success rate: {results['success_rate']:.2f}%")
```

### Input File Formats

The tool supports various input file formats:

#### CSV Files
```csv
url,company
https://example.com,Example Corp
https://test.com,Test Inc
```

#### Excel Files (.xlsx, .xls)
- Can contain multiple sheets
- Automatically detects URL columns

#### Text Files (.txt)
```
https://example.com
https://test.com
https://sample.org
```

#### Word Documents (.docx)
- Extracts URLs from paragraphs and tables

## 🔧 Configuration

### EmailScraper Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_selenium` | bool | True | Use Selenium for dynamic content |
| `use_proxies` | bool | False | Enable proxy rotation |
| `use_social_scraping` | bool | True | Scrape social media profiles |
| `max_internal_pages` | int | 5 | Max internal pages to scrape |
| `output_format` | str | 'excel' | Output format ('csv', 'excel', 'both') |

### Output Files

The tool generates several output files:

1. **Email_Results.csv/xlsx**: Main results with all found emails
2. **Summary.csv/xlsx**: Statistics and summary information
3. **Social_Media_Results.csv/xlsx**: Results from social media scraping
4. **Failed_URLs.csv/xlsx**: URLs that failed to scrape
5. **detailed_report.txt**: Comprehensive text report

## 🧪 Testing

### Quick Test

1. Use the provided test file:
   ```bash
   python main.py test_urls.txt
   ```

2. Check the `output/` directory for results

### Unit Tests

Run the unit tests (when implemented):
```bash
pytest tests/
```

## 📊 Output Format

### Main Results
| Column | Description |
|--------|-------------|
| URL | The scraped URL |
| Email | Found email address |
| Source_Page | Page where email was found |
| Status | Success/Failed |
| Scraping_Method | Requests/Selenium |
| Error | Error message (if failed) |
| Timestamp | When the scraping occurred |

### Summary Statistics
- Total URLs processed
- Success/failure rates
- Email counts by domain
- Performance metrics

## 🔒 Ethical Considerations

- **Respect robots.txt**: The tool respects website robots.txt files
- **Rate limiting**: Built-in delays between requests
- **User-agent rotation**: Avoids detection
- **Proxy support**: Can use proxies to distribute requests
- **Error handling**: Graceful handling of failures

## 🚨 Legal Disclaimer

This tool is for educational and legitimate business purposes only. Users are responsible for:
- Complying with website terms of service
- Respecting robots.txt files
- Following applicable laws and regulations
- Using the tool responsibly and ethically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Download ChromeDriver and add to PATH
   - Or place in project directory

2. **Selenium errors**
   - Ensure Chrome browser is installed
   - Check ChromeDriver version compatibility

3. **Import errors**
   - Activate virtual environment
   - Install all requirements: `pip install -r requirements.txt`

4. **Proxy issues**
   - Free proxies may be unreliable
   - Consider using paid proxy services for production

### Performance Tips

- Use `--no-social` for faster scraping without social media
- Reduce `--internal-pages` for quicker results
- Use `--proxies` for better success rates
- Consider running during off-peak hours

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue on the repository

---

**Happy Scraping! 🕷️📧** 