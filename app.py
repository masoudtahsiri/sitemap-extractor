from flask import Flask, render_template, request, jsonify, send_file
import requests
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import csv
from urllib.parse import urljoin, urlparse
import time

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_urls():
    try:
        data = request.json
        sitemap_url = data.get('sitemap_url', '').strip()
        
        if not sitemap_url:
            return jsonify({'error': 'Sitemap URL is required'}), 400
        
        # Validate URL
        parsed = urlparse(sitemap_url)
        if not parsed.scheme or not parsed.netloc:
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Parse sitemap and extract URLs
        urls = parse_sitemap_url(sitemap_url)
        
        if not urls:
            return jsonify({'error': 'No URLs found in sitemap'}), 404
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['URL'])  # Header
        for url in urls:
            writer.writerow([url])
        
        # Convert to BytesIO for file download
        csv_bytes = BytesIO()
        csv_bytes.write(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        return jsonify({
            'success': True,
            'url_count': len(urls),
            'csv_data': output.getvalue()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_csv():
    try:
        data = request.json
        csv_data = data.get('csv_data', '')
        
        if not csv_data:
            return jsonify({'error': 'No CSV data provided'}), 400
        
        # Create file in memory
        csv_bytes = BytesIO()
        csv_bytes.write(csv_data.encode('utf-8'))
        csv_bytes.seek(0)
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='sitemap_urls.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

