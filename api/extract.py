"""Vercel serverless function for extracting URLs from sitemap"""
import json
import csv
from io import StringIO
from urllib.parse import urlparse
from sitemap_parser import parse_sitemap_url

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Parse request body - handle different request formats
        body = ''
        if hasattr(request, 'body'):
            body = request.body
        elif isinstance(request, dict):
            body = request.get('body', '')
        
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        elif body is None:
            body = ''
        
        if body:
            try:
                data = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                data = {}
        else:
            data = {}
        
        sitemap_url = data.get('sitemap_url', '').strip()
        
        if not sitemap_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': 'Sitemap URL is required'})
            }
        
        # Validate URL
        parsed = urlparse(sitemap_url)
        if not parsed.scheme or not parsed.netloc:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': 'Invalid URL format'})
            }
        
        # Parse sitemap and extract URLs
        urls = parse_sitemap_url(sitemap_url)
        
        if not urls:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': 'No URLs found in sitemap'})
            }
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['URL'])  # Header
        for url in urls:
            writer.writerow([url])
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                'success': True,
                'url_count': len(urls),
                'csv_data': output.getvalue()
            })
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in extract handler: {error_details}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }

