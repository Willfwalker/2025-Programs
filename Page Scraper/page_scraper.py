import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
import time
from collections import deque

class PageScraper:
    def __init__(self, base_url, max_depth=1, restrict_domain=True, delay=0.5):
        self.base_url = base_url
        self.max_depth = max_depth
        self.restrict_domain = restrict_domain
        self.delay = delay
        self.links = set()
        self.images = set()
        self.visited_urls = set()
        self.base_domain = urlparse(base_url).netloc

    def is_same_domain(self, url):
        """Check if URL belongs to the same domain as base_url"""
        return urlparse(url).netloc == self.base_domain

    def scrape(self):
        """Start the scraping process"""
        print(f"Starting recursive scrape from {self.base_url} with max depth {self.max_depth}")
        if self.restrict_domain:
            print(f"Restricting to domain: {self.base_domain}")

        # Initialize queue with (url, depth) tuples
        queue = deque([(self.base_url, 0)])
        self.visited_urls.add(self.base_url)

        while queue:
            current_url, depth = queue.popleft()
            print(f"Scraping {current_url} (depth {depth}/{self.max_depth})")

            # Scrape the current page
            page_links, page_images = self._scrape_page(current_url)

            # Add discovered links and images to our collections
            self.links.update(page_links)
            self.images.update(page_images)

            # If we haven't reached max depth, add new links to the queue
            if depth < self.max_depth:
                for link in page_links:
                    # Skip if we've already visited this URL
                    if link in self.visited_urls:
                        continue

                    # Skip if domain restriction is enabled and link is from a different domain
                    if self.restrict_domain and not self.is_same_domain(link):
                        continue

                    # Add to queue and mark as visited
                    queue.append((link, depth + 1))
                    self.visited_urls.add(link)

            # Be polite and wait between requests
            time.sleep(self.delay)

    def _scrape_page(self, url):
        """Scrape a single page and return discovered links and images"""
        page_links = set()
        page_images = set()

        try:
            # Fetch the webpage
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and process all links
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    # Skip fragment identifiers and javascript links
                    if absolute_url.startswith(('http://', 'https://')):
                        page_links.add(absolute_url)

            # Extract and process all images
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    absolute_url = urljoin(url, src)
                    page_images.add(absolute_url)

            return page_links, page_images

        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return set(), set()

    def save_index(self, filename='index.json'):
        # Create index with metadata
        index = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'config': {
                'max_depth': self.max_depth,
                'restrict_domain': self.restrict_domain,
                'domain': self.base_domain
            },
            'stats': {
                'total_links': len(self.links),
                'total_images': len(self.images),
                'pages_visited': len(self.visited_urls)
            },
            'visited_urls': list(self.visited_urls),
            'links': list(self.links),
            'images': list(self.images)
        }

        # Save to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

        print(f"Results saved to {filename}")

def main():
    # Get user input
    url = input("Enter the website URL to scrape: ")

    # Get max depth
    max_depth_input = input("Enter maximum crawl depth (default: 1): ").strip()
    max_depth = int(max_depth_input) if max_depth_input.isdigit() else 1

    # Get domain restriction preference
    restrict_domain_input = input("Restrict to same domain? (y/n, default: y): ").strip().lower()
    restrict_domain = restrict_domain_input != 'n'

    # Get delay between requests
    delay_input = input("Delay between requests in seconds (default: 0.5): ").strip()
    try:
        delay = float(delay_input) if delay_input else 0.5
    except ValueError:
        delay = 0.5

    # Create and configure the scraper
    scraper = PageScraper(url, max_depth=max_depth, restrict_domain=restrict_domain, delay=delay)

    # Start scraping
    print(f"\nStarting scraper...")
    scraper.scrape()

    # Print summary
    print("\n--- Scraping Complete ---")
    print(f"Pages visited: {len(scraper.visited_urls)}")
    print(f"Unique links found: {len(scraper.links)}")
    print(f"Unique images found: {len(scraper.images)}")

    # Save results
    filename = input("Enter filename to save results (default: index.json): ").strip()
    if not filename:
        filename = "index.json"
    scraper.save_index(filename)

if __name__ == "__main__":
    main()
