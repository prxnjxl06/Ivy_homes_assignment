# api_explorer.py
import requests

BASE_URL = "http://35.200.185.69:8000/v1/autocomplete"

def query_api(prefix):
    response = requests.get(BASE_URL, params={"query": prefix})
    print(f"\nQuery: {prefix}")
    print(f"Status Code: {response.status_code}")
    print("Response:", response.text)

if __name__ == "__main__":
    prefixes = [
        "a", "aa", "aaa", "aab", "aabd", "aabdk", "aabdkn", "aabdknl", "aabdknlv", "aabdknlvk", "aabdknlvkc"
    ]
    for p in prefixes:
        query_api(p)
