# Universal Data Extractor API

A lightweight web-based data extraction tool built with Python and Flask. This application allows users to fetch and format structured data directly into a clean, copy-pasteable format for spreadsheet applications like Microsoft Excel or Google Sheets.

## Features

- **Web API Interface**: Simple query parameter-based data fetching (`?page=1`).
- **Cloudflare/Bot Bypass**: Built with `curl_cffi` to perfectly impersonate a real browser's TLS fingerprint, preventing 403 blocks from target servers.
- **Secure Setup**: Target URLs are stored securely in environment variables, keeping the source code generic and clean for public repositories.
- **Excel-Friendly Output**: Data is rendered in a standard HTML table format that can be directly copied and pasted into Excel with perfect formatting.

## Deployment

This application is designed to be deployed on platforms like **Render**, **Heroku**, or any cloud provider supporting Python/Flask.

### Deploy to Render
1. Connect your GitHub repository to Render.
2. Select "Web Service".
3. Use the following settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. **Environment Variables**: You MUST add the following environment variable in your Render dashboard:
   - **Key**: `TARGET_BASE_URL`
   - **Value**: `https://example.com/source/contractors?page=` (Replace with your actual target URL, ending right before the page number).

## Usage

Once deployed and the environment variable is set, access the API using the `page` parameter:

```
https://your-app-name.onrender.com/?page=1
```

The application will extract the relevant data points for that page and display them in a table.

## Local Development

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your environment variable:
   ```bash
   export TARGET_BASE_URL="https://example.com/source/contractors?page="
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open `http://localhost:5000/?page=1` in your browser.

## License
MIT
