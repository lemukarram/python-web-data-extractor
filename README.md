# Universal Data Extractor API

A lightweight web-based data extraction tool built with Python and Flask. This application allows users to fetch and format structured data from specified source URLs directly into a clean, copy-pasteable format for spreadsheet applications like Microsoft Excel or Google Sheets.

## Features

- **Web API Interface**: Simple query parameter-based data fetching.
- **Validation**: Built-in validation to ensure source URLs are supported.
- **Excel-Friendly Output**: Data is rendered in a standard HTML table format that can be directly copied and pasted into Excel with perfect formatting.
- **Efficient Scraping**: Optimized to handle data extraction with proper headers and session management.

## Deployment

This application is designed to be deployed on platforms like **Render**, **Heroku**, or any cloud provider supporting Python/Flask.

### Deploy to Render
1. Connect your GitHub repository to Render.
2. Select "Web Service".
3. Use the following settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

## Usage

Once deployed, access the API using the `fetch` parameter:

```
https://your-app-name.onrender.com/?fetch=SOURCE_URL
```

The application will validate the `SOURCE_URL`, extract the relevant data points, and display them in a table.

## Local Development

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open `http://localhost:5000` in your browser.

## License
MIT
