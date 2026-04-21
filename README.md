# Universal Data Extractor Tool

This is a simple tool to extract information from web pages and save it into an Excel-friendly CSV file. It is designed to be run on your personal computer, which helps avoid being blocked by websites.

## How to Set Up (One-Time Only)

Follow these steps if you have never run a Python script before.

### Step 1: Install Python
1. Go to [python.org/downloads](https://www.python.org/downloads/).
2. Click the **Download Python** button.
3. **Important:** When installing, make sure to check the box that says **"Add Python to PATH"** before clicking "Install Now".

### Step 2: Download this Tool
1. Click the green **"Code"** button on this GitHub page.
2. Select **"Download ZIP"**.
3. Extract (unzip) the folder to your Desktop or anywhere you like.

### Step 3: Install Required Libraries
1. Open your computer's terminal:
   - **Windows**: Search for `cmd` or `Command Prompt` in your start menu.
   - **Mac**: Search for `Terminal` in Spotlight (Command + Space).
2. Copy and paste the command below that matches your computer:
   - **Windows**: `pip install curl-cffi beautifulsoup4 requests`
   - **Mac / Linux**: `python3 -m pip install curl-cffi beautifulsoup4 requests`

---

## How to Run the Tool

1. Open your terminal (as shown in Step 3 above).
2. Navigate to the folder where you extracted the tool. For example:
   ```bash
   cd Desktop/python-web-data-extractor
   ```
3. Run the script:
   ```bash
   python extractor.py
   ```
   *(Note: On some Macs, you might need to type `python3 extractor.py` instead)*

4. The script will ask you to **"Please paste the full URL"**.
5. Copy the URL from your browser (e.g., `https://.../path?page=3`) and paste it into the terminal, then press Enter.
6. Once finished, a new file named after the page number (e.g., `3.csv`) will appear in the same folder. You can open this file directly with **Microsoft Excel**.

## Troubleshooting
- **403 Error**: If you see this, the website is blocking the request. Try using a VPN or checking if you can access the website normally in your browser.
- **Python not found**: Ensure you checked the "Add Python to PATH" box during installation. If not, reinstall Python and make sure it's checked.

## License
MIT
