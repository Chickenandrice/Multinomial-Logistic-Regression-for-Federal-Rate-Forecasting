import requests
import pandas as pd
from dotenv import load_dotenv
import os 

load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

BASE_URL = "https://api.stlouisfed.org/fred/series/search"

def search_fred(query):
    # query fred via api
    params = {
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "search_text": query,
        "limit": 5,
        "sort_order": "desc"
    }
    response = requests.get(BASE_URL, params=params)

    data = response.json()["seriess"]

    df = pd.DataFrame(data)
    return df[["id", "title", "frequency_short", "units_short", "observation_start", "observation_end", "popularity"]]

if __name__ == "__main__":
    keyword = input("Search data: ")
    results = search_fred(keyword)

    print("\nSearch Results:\n")
    print(results.to_string(index=False))
