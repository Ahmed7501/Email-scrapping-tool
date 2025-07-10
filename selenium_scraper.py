import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time, random

class SeleniumScraper:
    def __init__(self, proxy=None, user_agent=None, headless=True):
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        if user_agent:
            options.add_argument(f'--user-agent={user_agent}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = uc.Chrome(options=options)
        self.driver.set_page_load_timeout(60)

    def get_page(self, url):
        try:
            self.driver.get(url)
            self._human_scroll()
            time.sleep(random.uniform(2, 4))
            html = self.driver.page_source
            title = self.driver.title
            meta_desc = ''
            try:
                meta_desc = self.driver.find_element(By.XPATH, '//meta[@name="description"]').get_attribute('content')
            except Exception:
                pass
            return html, title, meta_desc
        except Exception as e:
            return None, None, str(e)

    def _human_scroll(self):
        # Simulate human-like scrolling
        body = self.driver.find_element(By.TAG_NAME, 'body')
        for _ in range(random.randint(2, 5)):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.5, 1.2))

    def close(self):
        self.driver.quit() 