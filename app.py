from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure secret key

def get_most_recent_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching the URL: {e}", None

    soup = BeautifulSoup(response.text, 'html.parser')
    # Regex pattern for filenames like: Pandora211s1_Agam_YYYYMMDD_L0.txt.bz2
    pattern = re.compile(r"Pandora211s1_Agam_(\d{8})_L0\.txt\.bz2")

    files = []
    for link in soup.find_all('a'):
        # Check both the href attribute and the link text
        file_candidate = link.get('href') or link.get_text()
        if file_candidate:
            match = pattern.search(file_candidate)
            if match:
                date_str = match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    files.append((date_obj, file_candidate))
                except ValueError:
                    continue

    if files:
        # Sort by date descending to get the most recent file first
        files.sort(key=lambda x: x[0], reverse=True)
        return None, files[0][1]
    else:
        return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        website_url = request.form.get("website_url")
        error, result = get_most_recent_file(website_url)
        if not result and not error:
            error = "No matching file found."
    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
