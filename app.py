import requests
from bs4 import BeautifulSoup
import time
import re
import os
from flask import Flask, request, render_template_string
from urllib.parse import unquote, urlparse, parse_qsl, urlencode

app = Flask(__name__)

# Realistic headers to bypass basic bot detection (403 errors)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

def decode_cloudflare_email(encoded_string):
    try:
        r = int(encoded_string[:2], 16)
        email = ''.join([chr(int(encoded_string[i:i+2], 16) ^ r) for i in range(2, len(encoded_string), 2)])
        return email
    except Exception:
        return "N/A"

def get_email_from_detail(detail_url, session):
    try:
        time.sleep(0.5) # Slightly longer delay to be safer
        response = session.get(detail_url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            email_element = soup.find(class_='__cf_email__')
            if email_element and email_element.get('data-cfemail'):
                return decode_cloudflare_email(email_element.get('data-cfemail'))
            
            info_boxes = soup.find_all('div', class_='info-box')
            for box in info_boxes:
                name = box.find('div', class_='info-name')
                if name and 'Email' in name.text:
                    val = box.find('div', class_='info-value')
                    if val:
                        return val.text.strip()
        return "N/A"
    except Exception:
        return "N/A"

def scrape_page_data(url):
    session = requests.Session()
    try:
        # Initial request to the page
        response = session.get(url, headers=HEADERS, timeout=25)
        if response.status_code != 200:
            return None, f"Failed to fetch page: {response.status_code}. The site might be blocking the request."
        
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all(class_='section-card')
        
        if not cards:
            return None, "No data cards found on the page. The page structure might have changed or the URL is incorrect."

        page_data = []
        for card in cards:
            name_el = card.find('h2', class_='card-title')
            if not name_el: continue
            
            name = name_el.text.strip()
            detail_link = name_el.find('a')['href']
            
            size = "N/A"
            city = "N/A"
            info_values = card.find_all('div', class_='info-box')
            for box in info_values:
                box_name = box.find('div', class_='info-name')
                if box_name and 'Company Size' in box_name.text:
                    box_val = box.find('div', class_='info-value')
                    if box_val: size = box_val.text.strip()
                
                if box_name and 'City' in box_name.text:
                    box_val = box.find('div', class_='info-value')
                    if box_val: 
                        city = box_val.text.strip().replace('\n', '').replace('  ', ' ')
            
            email = get_email_from_detail(detail_link, session)
            
            page_data.append({
                "Company Name": name,
                "Email": email,
                "City": city,
                "Company Size": size
            })
        return page_data, None
    except Exception as e:
        return None, f"Extraction Error: {str(e)}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Universal Data Extractor</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px auto; max-width: 1200px; line-height: 1.6; color: #333; }
        .container { padding: 20px; border: 1px solid #eee; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 14px; }
        th, td { border: 1px solid #dfe6e9; padding: 12px; text-align: left; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f8f9fa; }
        tr:hover { background-color: #f1f2f6; }
        .instructions { background: #fdfdfd; padding: 20px; border-left: 5px solid #3498db; margin-bottom: 30px; }
        code { background: #eee; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
        .error { background: #fab1a0; color: #c0392b; padding: 15px; border-radius: 5px; margin-top: 20px; font-weight: bold; }
        .success-msg { color: #27ae60; font-weight: bold; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Extraction Tool</h1>
        
        {% if not data and not error %}
        <div class="instructions">
            <h3>How to use:</h3>
            <p>Append the <code>fetch</code> parameter to the URL with the target page URL you want to extract.</p>
            <p><strong>Example:</strong><br>
            <code>?fetch=https://example-source.com/data?page=1</code></p>
        </div>
        {% endif %}

        {% if error %}
            <div class="error">
                Status: {{ error }}
            </div>
            <p><em>Note: A 403 error usually means the source website is blocking cloud hosting IPs (like Render). Try again in a few minutes or check the source URL.</em></p>
        {% endif %}

        {% if data %}
            <div class="success-msg">Successfully extracted {{ data|length }} records.</div>
            <p>You can now highlight the table below, copy it, and paste it directly into Excel or Google Sheets.</p>
            <table>
                <thead>
                    <tr>
                        <th>Company Name</th>
                        <th>Email</th>
                        <th>City</th>
                        <th>Company Size</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        <td>{{ row['Company Name'] }}</td>
                        <td>{{ row['Email'] }}</td>
                        <td>{{ row['City'] }}</td>
                        <td>{{ row['Company Size'] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Robustly get the 'fetch' URL. 
    # Flask sometimes splits query parameters if they aren't encoded.
    # We reconstruct the intended URL from all parameters.
    fetch_url = request.args.get('fetch')
    if not fetch_url:
        return render_template_string(HTML_TEMPLATE)

    # Reconstruct the URL if it contained a '?' that was split into other args
    all_args = list(request.args.items())
    if len(all_args) > 1:
        # The first arg is 'fetch'. The rest likely belong to the fetch_url.
        base_fetch = all_args[0][1]
        extra_params = []
        for i in range(1, len(all_args)):
            extra_params.append(f"{all_args[i][0]}={all_args[i][1]}")
        
        separator = '&' if '?' in base_fetch else '?'
        fetch_url = f"{base_fetch}{separator}{'&'.join(extra_params)}"

    # Validation: Use a generic pattern to hide the specific target domain
    # This matches: m (4-6 chars) l .org / ... / contractors?page=X
    default_pattern = r'^https://m.{4,6}l\.org/.+/contractors\?page=\d+$'
    allowed_pattern = os.environ.get('ALLOWED_URL_PATTERN', default_pattern)
    
    if not re.match(allowed_pattern, fetch_url):
        return render_template_string(HTML_TEMPLATE, error="Invalid or unauthorized Source URL. Please provide a valid page URL.")

    data, error = scrape_page_data(fetch_url)
    return render_template_string(HTML_TEMPLATE, data=data, error=error)

if __name__ == '__main__':
    # Use port from environment for deployment flexibility
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
