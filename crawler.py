from urllib.parse import urljoin

def get_internal_pages(base_url):
    # Return common internal pages to try
    return [urljoin(base_url, path) for path in ['/contact', '/about', '/team']] 