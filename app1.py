from flask import Flask, render_template, request
import os
import requests
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the GitHub API key from the environment variable
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Function to search GitHub for code related to the company
def search_github(company, keyword):
    # URL encode to handle special characters
    company_encoded = urllib.parse.quote_plus(company)
    keyword_encoded = urllib.parse.quote_plus(keyword)

    # GitHub Code Search API URL (searching globally)
    url = f"https://api.github.com/search/code?q={keyword_encoded}+{company_encoded}"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }

    # API request
    response = requests.get(url, headers=headers)

    # Debugging: Print API response status
    print("GitHub API Response Status Code:", response.status_code)

    if response.status_code == 200:
        results = response.json().get('items', [])
        print("GitHub API Response JSON:", results)  # Debugging
        return results
    else:
        print("GitHub API Error:", response.status_code, response.text)
        return []

# Route to handle GET and POST requests
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        company = request.form["company"]
        keyword = request.form["keyword"]

        # Debugging: Print company and keyword
        print("Company:", company)
        print("Keyword:", keyword)

        # Call search function
        results = search_github(company, keyword)

        # Debugging: Print results
        print("Results:", results)

        # Render results page
        return render_template("results.html", results=results, company=company, keyword=keyword)

    return render_template("index.html")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
