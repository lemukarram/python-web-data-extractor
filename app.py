import os
import time
import re
from urllib.parse import urljoin
from flask import Flask, request, render_template_string

# curl_cffi acts as a drop-in replacement for requests but impersonates browser TLS fingerprints perfectly
from curl_cffi import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def decode_cloudflare_email(encoded_string):
    try:
        r = int(encoded_string[:2], 16)
        email = ''.join([chr(int(encoded_string[i:i+2], 16) ^ r) for i in range(2, len(encoded_string), 2)])
        return email
    except Exception:
        return "N/A"

def get_email_from_detail(detail_url, session):
    try:
        time.sleep(0.5) # Gentle delay between requests
        response = session.get(detail_url, timeout=15)
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
    # impersonate="chrome110" makes this request appear exactly like a real Chrome browser, 
    # helping to bypass strict Cloudflare or 403 blocks.
    session = requests.Session(impersonate="chrome110")
    try:
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            return None, f"Failed to fetch page: HTTP {response.status_code}. The site might still be blocking cloud hosting."
        
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all(class_='section-card')
        
        if not cards:
            return None, "No data found on this page. Either the page is empty, or the HTML structure of the target site has changed."

        page_data = []
        for card in cards:
            name_el = card.find('h2', class_='card-title')
            if not name_el: continue
            
            name = name_el.text.strip()
            
            detail_link = None
            a_tag = name_el.find('a')
            if a_tag and 'href' in a_tag.attrs:
                detail_link = urljoin(url, a_tag['href'])
            
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
            
            email = "N/A"
            if detail_link:
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
        code { background: #eee; padding: 2px 5px; border-radius: 3px; font-family: monospace; font-size: 1.1em; }
        .error { background: #fab1a0; color: #c0392b; padding: 15px; border-radius: 5px; margin-top: 20px; font-weight: bold; }
        .success-msg { color: #27ae60; font-weight: bold; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Extraction Tool</h1>
        
        {% if not setup_complete %}
            <div class="error">
                Setup Incomplete: You must set the <code>TARGET_BASE_URL</code> environment variable in your Render dashboard.
            </div>
            <p>Example value: <code>https://example.com/en/contractors?page=</code></p>
        {% elif not data and not error %}
        <div class="instructions">
            <h3>How to use:</h3>
            <p>Append the <code>page</code> parameter to the URL to fetch data for that specific page number.</p>
            <p><strong>Example:</strong><br>
            <code>/?page=1</code></p>
        </div>
        {% endif %}

        {% if error %}
            <div class="error">
                Status: {{ error }}
            </div>
        {% endif %}

        {% if data %}
            <div class="success-msg">Successfully extracted {{ data|length }} records for page {{ current_page }}.</div>
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
    # Read the base URL from the environment. 
    # The URL should look like "https://target-domain.com/path?page="
    target_base_url = os.environ.get('TARGET_BASE_URL')
    
    if not target_base_url:
        return render_template_string(HTML_TEMPLATE, setup_complete=False)

    page_num = request.args.get('page')
    
    if not page_num:
        return render_template_string(HTML_TEMPLATE, setup_complete=True)

    # Validate that page is a number
    if not page_num.isdigit():
        return render_template_string(HTML_TEMPLATE, setup_complete=True, error="Invalid page number. It must be an integer.")

    # Construct the final URL securely without passing domains via query params
    fetch_url = f"{target_base_url}{page_num}"

    data, error = scrape_page_data(fetch_url)
    return render_template_string(HTML_TEMPLATE, setup_complete=True, data=data, error=error, current_page=page_num)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
