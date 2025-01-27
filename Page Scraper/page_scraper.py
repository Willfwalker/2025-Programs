import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime

class PageScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.links = set()
        self.images = set()
        
    def scrape(self):
        try:
            # Fetch the webpage
            response = requests.get(self.base_url)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and process all links
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    absolute_url = urljoin(self.base_url, href)
                    self.links.add(absolute_url)
            
            # Extract and process all images
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    absolute_url = urljoin(self.base_url, src)
                    self.images.add(absolute_url)
                    
        except requests.RequestException as e:
            print(f"Error scraping {self.base_url}: {e}")
    
    def save_index(self, filename='index.json'):
        # Create index with metadata
        index = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'stats': {
                'total_links': len(self.links),
                'total_images': len(self.images)
            },
            'links': list(self.links),
            'images': list(self.images)
        }
        
        # Save to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

def main():
    # Example usage
    url = input("Enter the website URL to scrape: ")
    scraper = PageScraper(url)
    print(f"Scraping {url}...")
    scraper.scrape()
    
    print(f"Found {len(scraper.links)} unique links")
    print(f"Found {len(scraper.images)} unique images")
    
    scraper.save_index()
    print("Results saved to index.json")

if __name__ == "__main__":
    main()
