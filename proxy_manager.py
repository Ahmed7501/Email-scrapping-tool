import random

class ProxyManager:
    def __init__(self, proxies=None):
        self.proxies = proxies or []
        self.index = 0

    def get_proxy(self):
        if not self.proxies:
            return None
        # Rotate proxies randomly or round-robin
        return random.choice(self.proxies) 