import os
import sys
import subprocess
import time
import re
import csv
from urllib.parse import urlparse, parse_qs, urljoin

def install_dependencies():
    """Automatically detects missing libraries and installs them based on the OS."""
    required = {'curl-cffi', 'beautifulsoup4', 'requests'}
    
    # Try to import them to see if they are missing
    missing = []
    try: import curl_cffi
    except ImportError: missing.append('curl-cffi')
    try: import bs4
    except ImportError: missing.append('beautifulsoup4')
    try: import requests
    except ImportError: missing.append('requests')

    if missing:
        print(f"\n[!] Missing required components: {', '.join(missing)}")
        print("[+] Starting automatic installation, please wait...")
        
        # Determine the correct pip command based on the OS/Python environment
        # Mac/Linux usually need 'python3 -m pip', Windows usually just 'pip'
        pip_cmd = [sys.executable, "-m", "pip", "install"] + missing
        
        try:
            subprocess.check_call(pip_cmd)
            print("[SUCCESS] All components installed successfully!\n")
            # Restart the script to load the newly installed libraries
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            print(f"\n[!] Automatic installation failed: {e}")
            print(f"[!] Please try running this manually: {' '.join(pip_cmd)}")
            sys.exit(1)

# Run the installer before anything else
install_dependencies()

# Now we can safely import the libraries
from curl_cffi import requests
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
        time.sleep(1)
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

def scrape_page(url):
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    page_num = params.get('page', ['unknown'])[0]
    filename = f"{page_num}.csv"

    print(f"\n[+] Connecting to the server...")
    session = requests.Session(impersonate="chrome110")
    
    try:
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            print(f"[!] Error: Status {response.status_code}. Site might be blocking you.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all(class_='section-card')
        
        if not cards:
            print("[!] No data found. Please check the URL.")
            return

        print(f"[+] Found {len(cards)} records. Extracting details...")
        
        page_data = []
        for index, card in enumerate(cards, 1):
            name_el = card.find('h2', class_='card-title')
            if not name_el: continue
            
            name = name_el.text.strip()
            print(f"    ({index}/{len(cards)}) {name[:40]}...")
            
            detail_link = None
            a_tag = name_el.find('a')
            if a_tag and 'href' in a_tag.attrs:
                detail_link = urljoin(url, a_tag['href'])
            
            size = "N/A"
            city = "N/A"
            info_boxes = card.find_all('div', class_='info-box')
            for box in info_boxes:
                box_name = box.find('div', class_='info-name')
                if box_name:
                    if 'Company Size' in box_name.text:
                        val = box.find('div', class_='info-value')
                        if val: size = val.text.strip()
                    elif 'City' in box_name.text:
                        val = box.find('div', class_='info-value')
                        if val: city = val.text.strip().replace('\n', '').replace('  ', ' ')
            
            email = "N/A"
            if detail_link:
                email = get_email_from_detail(detail_link, session)
            
            page_data.append({
                "Company Name": name,
                "Email": email,
                "City": city,
                "Company Size": size
            })

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Company Name", "Email", "City", "Company Size"])
            writer.writeheader()
            writer.writerows(page_data)

        print(f"\n[SUCCESS] Data saved to: {filename}")
        print(f"[TIP] You can open this file in Excel.")

    except Exception as e:
        print(f"\n[!] Error: {str(e)}")

def main():
    print("========================================")
    print("       UNIVERSAL DATA EXTRACTOR")
    print("========================================")
    
    target_url = input("\nPlease paste the full URL:\n> ").strip()
    if not target_url.startswith("http"):
        print("[!] Invalid URL.")
        return
    
    scrape_page(target_url)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Stopped.")
    input("\nPress Enter to exit...")
