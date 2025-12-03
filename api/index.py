from flask import Flask, request, jsonify, Response
import csv
from io import StringIO
from urllib.parse import urlparse
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sitemap URL Extractor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 2em; text-align: center; }
        .subtitle { color: #666; text-align: center; margin-bottom: 30px; font-size: 0.95em; }
        .form-group { margin-bottom: 25px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input[type="url"] {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="url"]:focus { outline: none; border-color: #667eea; }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-download {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            margin-top: 15px;
            display: none;
        }
        .btn-download:hover:not(:disabled) { box-shadow: 0 5px 20px rgba(17, 153, 142, 0.4); }
        .status { margin-top: 20px; padding: 15px; border-radius: 10px; display: none; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .loader { display: none; text-align: center; margin-top: 20px; }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .example { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px; font-size: 0.9em; color: #666; }
        .example strong { color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ Sitemap URL Extractor</h1>
        <p class="subtitle">Extract all URLs from any sitemap and export to CSV</p>
        <form id="sitemapForm">
            <div class="form-group">
                <label for="sitemapUrl">Sitemap URL</label>
                <input type="url" id="sitemapUrl" name="sitemapUrl" placeholder="https://example.com/sitemap.xml" required>
            </div>
            <button type="submit" class="btn" id="submitBtn">Extract URLs</button>
            <button type="button" class="btn btn-download" id="downloadBtn">📥 Download CSV</button>
        </form>
        <div class="loader" id="loader">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">Extracting URLs from sitemap...</p>
        </div>
        <div class="status" id="status"></div>
        <div class="example">
            <strong>Example sitemap URLs:</strong><br>
            • https://www.google.com/sitemap.xml<br>
            • https://example.com/sitemap.xml
        </div>
    </div>
    <script>
        const form = document.getElementById('sitemapForm');
        const submitBtn = document.getElementById('submitBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const loader = document.getElementById('loader');
        const status = document.getElementById('status');
        let csvData = '';

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const sitemapUrl = document.getElementById('sitemapUrl').value.trim();
            if (!sitemapUrl) { showStatus('Please enter a sitemap URL', 'error'); return; }
            loader.style.display = 'block';
            status.style.display = 'none';
            downloadBtn.style.display = 'none';
            submitBtn.disabled = true;
            submitBtn.textContent = 'Extracting...';
            try {
                const response = await fetch('/api/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sitemap_url: sitemapUrl })
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Failed to extract URLs');
                csvData = data.csv_data;
                showStatus('✅ Successfully extracted ' + data.url_count + ' URLs!', 'success');
                downloadBtn.style.display = 'block';
            } catch (error) {
                showStatus('❌ Error: ' + error.message, 'error');
            } finally {
                loader.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Extract URLs';
            }
        });

        downloadBtn.addEventListener('click', () => {
            if (!csvData) { showStatus('No data to download', 'error'); return; }
            const blob = new Blob([csvData], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'sitemap_urls.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        });

        function showStatus(message, type) {
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }
    </script>
</body>
</html>'''

def parse_sitemap_url(url, max_sitemaps=50):
    """Parse a sitemap URL and extract all URLs recursively"""
    urls = set()
    visited_sitemaps = set()
    
    def fetch_and_parse(sitemap_url, depth=0):
        # Limit recursion and number of sitemaps
        if sitemap_url in visited_sitemaps or len(visited_sitemaps) >= max_sitemaps or depth > 3:
            return
        visited_sitemaps.add(sitemap_url)
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(sitemap_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            if root.tag.endswith('sitemapindex'):
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        fetch_and_parse(loc.text, depth + 1)
            else:
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        urls.add(loc.text)
            
            if not urls and not root.tag.endswith('sitemapindex'):
                for url_elem in root.findall('.//url'):
                    loc = url_elem.find('loc')
                    if loc is not None and loc.text:
                        urls.add(loc.text)
            
            for sitemap in root.findall('.//sitemap'):
                loc = sitemap.find('loc')
                if loc is not None and loc.text:
                    fetch_and_parse(loc.text, depth + 1)
                    
        except Exception as e:
            print(f"Error processing {sitemap_url}: {e}")
    
    fetch_and_parse(url)
    return sorted(list(urls))

@app.route('/')
def home():
    return Response(HTML_CONTENT, mimetype='text/html')

@app.route('/api/extract', methods=['POST', 'OPTIONS'])
def extract():
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
            return jsonify({'error': 'Sitemap URL is required'}), 400
        
        parsed = urlparse(sitemap_url)
        if not parsed.scheme or not parsed.netloc:
            return jsonify({'error': 'Invalid URL format'}), 400
        
        urls = parse_sitemap_url(sitemap_url)
        
        if not urls:
            return jsonify({'error': 'No URLs found in sitemap'}), 404
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['URL'])
        for url in urls:
            writer.writerow([url])
        
        return jsonify({
            'success': True,
            'url_count': len(urls),
            'csv_data': output.getvalue()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
