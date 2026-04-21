import os
import time
import re
import csv
from urllib.parse import urlparse, parse_qs, urljoin

# Using curl_cffi to bypass advanced bot protection
try:
    from curl_cffi import requests
except ImportError:
    print("\n[!] Error: 'curl_cffi' library not found.")
    print("[!] Please run: pip install curl-cffi")
    exit(1)

from bs4 import BeautifulSoup

def decode_cloudflare_email(encoded_string):
    try:
        r = int(encoded_string[:2], 16)
        email = ''.join([chr(int(encoded_string[i:i+2], 16) ^ r) for i in range(2, len(encoded_string), 2)])
        return email
    except Exception:
        return "N/A"

def get_email_from_detail(detail_url, session):
    try:
        # Subtle delay to avoid being flagged
        time.sleep(1)
        response = session.get(detail_url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for Cloudflare protected email
            email_element = soup.find(class_='__cf_email__')
            if email_element and email_element.get('data-cfemail'):
                return decode_cloudflare_email(email_element.get('data-cfemail'))
            
            # Fallback to searching info boxes
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

def scrape_page(url):
    # Re-extracting page number for the filename
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    page_num = params.get('page', ['unknown'])[0]
    filename = f"{page_num}.csv"

    print(f"\n[+] Connecting to the server...")
    
    # Impersonate Chrome to bypass TLS fingerprinting and 403 errors
    session = requests.Session(impersonate="chrome110")
    
    try:
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"[!] Error: Server returned status code {response.status_code}")
            if response.status_code == 403:
                print("[!] The website is blocking the request. Try using a VPN or checking your internet connection.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all(class_='section-card')
        
        if not cards:
            print("[!] No data cards found on this page. Please verify the URL.")
            return

        print(f"[+] Found {len(cards)} records. Starting data extraction...")
        
        page_data = []
        for index, card in enumerate(cards, 1):
            name_el = card.find('h2', class_='card-title')
            if not name_el: continue
            
            name = name_el.text.strip()
            print(f"    ({index}/{len(cards)}) Extracting: {name[:40]}...")
            
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

        # Saving to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Company Name", "Email", "City", "Company Size"])
            writer.writeheader()
            writer.writerows(page_data)

        print(f"\n[SUCCESS] Data successfully saved to: {filename}")
        print(f"[TIP] You can now open {filename} directly in Excel.")

    except Exception as e:
        print(f"\n[!] A critical error occurred: {str(e)}")

def main():
    print("========================================")
    print("       UNIVERSAL DATA EXTRACTOR")
    print("========================================")
    
    target_url = input("\nPlease paste the full URL (e.g., https://.../path?page=3):\n> ").strip()
    
    if not target_url.startswith("http"):
        print("[!] Invalid URL. Please make sure it starts with http:// or https://")
        return

    # Basic check to ensure it has a page parameter
    if "page=" not in target_url:
        print("[!] Warning: No 'page=' parameter found in the URL. Output file will be named 'unknown.csv'.")
    
    scrape_page(target_url)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Script stopped by user.")
    input("\nPress Enter to exit...")
