# Sitemap URL Extractor

A web application that extracts all URLs from a sitemap (including sitemap index files) and exports them to a CSV file.

## Features

- ✅ Extract URLs from XML sitemaps
- ✅ Handle sitemap index files (recursively processes nested sitemaps)
- ✅ Export to CSV format
- ✅ Modern, responsive web interface
- ✅ Real-time extraction progress
- ✅ Deployable on Vercel

## Local Development

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Enter a sitemap URL (e.g., `https://example.com/sitemap.xml`)

4. Click "Extract URLs" to process the sitemap

5. Click "Download CSV" to save the URLs to a CSV file

## Deployment on Vercel

### Prerequisites

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Make sure you have a Vercel account (sign up at [vercel.com](https://vercel.com))

### Deploy

1. Navigate to the project directory:
```bash
cd "sitemap url extractor"
```

2. Deploy to Vercel:
```bash
vercel
```

3. Follow the prompts:
   - Link to existing project or create new
   - Confirm project settings
   - Deploy

4. Your app will be live at the provided Vercel URL!

### Alternative: Deploy via GitHub

1. Push your code to a GitHub repository
2. Import the repository in Vercel dashboard
3. Vercel will automatically detect the configuration and deploy

### Testing Locally with Vercel

You can test the Vercel deployment locally:
```bash
vercel dev
```

## Example Sitemap URLs

- `https://www.google.com/sitemap.xml`
- `https://example.com/sitemap.xml`
- `https://example.com/sitemap_index.xml`

## How It Works

The application:
1. Fetches the sitemap XML from the provided URL
2. Parses the XML to extract URLs
3. If it's a sitemap index, recursively processes all nested sitemaps
4. Collects all unique URLs
5. Exports them to a CSV file with a single "URL" column

## Project Structure

```
.
├── api/
│   ├── index.py          # Main page handler (Vercel)
│   └── extract.py        # Extract API endpoint (Vercel)
├── templates/
│   └── index.html        # Frontend (for local Flask)
├── app.py                # Flask app (for local development)
├── sitemap_parser.py     # Shared sitemap parsing logic
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md
```

## Requirements

- Python 3.7+
- Flask (for local development)
- requests
- Vercel account (for deployment)

