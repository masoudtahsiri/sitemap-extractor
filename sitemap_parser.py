"""Shared sitemap parsing utility"""
import requests
import xml.etree.ElementTree as ET

def parse_sitemap_url(url):
    """Parse a sitemap URL and extract all URLs recursively"""
    urls = set()
    visited_sitemaps = set()
    
    def fetch_and_parse(sitemap_url):
        """Recursively fetch and parse sitemap"""
        if sitemap_url in visited_sitemaps:
            return
        visited_sitemaps.add(sitemap_url)
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(sitemap_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Check if it's a sitemap index
            if root.tag.endswith('sitemapindex'):
                # It's a sitemap index, process each sitemap
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        # Recursively parse nested sitemap
                        fetch_and_parse(loc.text)
            else:
                # It's a regular sitemap, extract URLs
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        urls.add(loc.text)
            
            # Also handle non-namespaced XML (some sitemaps don't use namespaces)
            if not urls and not root.tag.endswith('sitemapindex'):
                for url_elem in root.findall('.//url'):
                    loc = url_elem.find('loc')
                    if loc is not None and loc.text:
                        urls.add(loc.text)
            
            # Handle sitemap index without namespace
            if root.tag.endswith('sitemapindex') or root.findall('.//sitemap'):
                for sitemap in root.findall('.//sitemap'):
                    loc = sitemap.find('loc')
                    if loc is not None and loc.text:
                        fetch_and_parse(loc.text)
            
        except requests.RequestException as e:
            print(f"Error fetching {sitemap_url}: {e}")
        except ET.ParseError as e:
            print(f"Error parsing XML from {sitemap_url}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {sitemap_url}: {e}")
    
    fetch_and_parse(url)
    return sorted(list(urls))

