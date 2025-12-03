from flask import Flask, request, jsonify
import csv
from io import StringIO
from urllib.parse import urlparse
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

def parse_sitemap_url(url):
    """Parse a sitemap URL and extract all URLs recursively"""
    urls = set()
    visited_sitemaps = set()
    
    def fetch_and_parse(sitemap_url):
        if sitemap_url in visited_sitemaps:
            return
        visited_sitemaps.add(sitemap_url)
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(sitemap_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Check if it's a sitemap index
            if root.tag.endswith('sitemapindex'):
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        fetch_and_parse(loc.text)
            else:
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        urls.add(loc.text)
            
            # Handle non-namespaced XML
            if not urls and not root.tag.endswith('sitemapindex'):
                for url_elem in root.findall('.//url'):
                    loc = url_elem.find('loc')
                    if loc is not None and loc.text:
                        urls.add(loc.text)
            
            # Handle sitemap index without namespace
            for sitemap in root.findall('.//sitemap'):
                loc = sitemap.find('loc')
                if loc is not None and loc.text:
                    fetch_and_parse(loc.text)
                    
        except Exception as e:
            print(f"Error processing {sitemap_url}: {e}")
    
    fetch_and_parse(url)
    return sorted(list(urls))

@app.route('/', methods=['POST', 'OPTIONS'])
def extract():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        data = request.get_json() or {}
        sitemap_url = data.get('sitemap_url', '').strip()
        
        if not sitemap_url:
            response = jsonify({'error': 'Sitemap URL is required'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        
        # Validate URL
        parsed = urlparse(sitemap_url)
        if not parsed.scheme or not parsed.netloc:
            response = jsonify({'error': 'Invalid URL format'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        
        # Parse sitemap and extract URLs
        urls = parse_sitemap_url(sitemap_url)
        
        if not urls:
            response = jsonify({'error': 'No URLs found in sitemap'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 404
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['URL'])
        for url in urls:
            writer.writerow([url])
        
        response = jsonify({
            'success': True,
            'url_count': len(urls),
            'csv_data': output.getvalue()
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        import traceback
        print(f"Error: {traceback.format_exc()}")
        response = jsonify({'error': str(e)})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500
