import requests
import time
import string
import csv
import os
import json

BASE_URL = "http://35.200.185.69:8000/v1/autocomplete"
RATE_LIMIT = 100
TIME_WINDOW = 60
PROGRESS_FILE = "progress.txt"
OUTPUT_FILE = "all_names.csv"

seen_names = set()
request_count = 0
start_time = time.time()

def load_seen_names():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            for line in f:
                seen_names.add(line.strip())

def save_names(names):
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for name in names:
            writer.writerow([name])

def save_progress(stack):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(stack, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return list(string.ascii_lowercase)  # Start from 'a' to 'z'

def rate_limited_request(prefix):
    global request_count, start_time
    backoff = 60
    while True:
        if request_count >= RATE_LIMIT:
            elapsed = time.time() - start_time
            if elapsed < TIME_WINDOW:
                wait_time = TIME_WINDOW - elapsed
                print(f"🕒 Rate limit hit. Sleeping {wait_time:.1f}s")
                time.sleep(wait_time)
            request_count = 0
            start_time = time.time()
        try:
            response = requests.get(BASE_URL, params={"query": prefix}, timeout=10)
            request_count += 1
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"⚠️ 429 Rate Limit - Sleeping {backoff}s...")
                time.sleep(backoff)
                backoff = min(backoff + 30, 300)
            else:
                print(f"❌ Error {response.status_code} for prefix '{prefix}'")
                return {"results": []}
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error for '{prefix}': {e}. Retrying in {backoff}s...")
            time.sleep(backoff)
            backoff = min(backoff + 30, 300)

def crawl():
    load_seen_names()
    stack = load_progress()
    print(f"▶️ Resuming with {len(stack)} prefixes. Already collected: {len(seen_names)} names.")

    while stack:
        prefix = stack.pop()
        result = rate_limited_request(prefix)
        results = result.get("results", [])
        count = result.get("count", 0)

        new_names = [name for name in results if name not in seen_names]
        if new_names:
            save_names(new_names)
            for name in new_names:
                seen_names.add(name)
            print(f"✅ Saved {len(new_names)} names from '{prefix}'")

        # If we hit the cap, go deeper (add a-z suffixes)
        if count == 10:
            for c in reversed(string.ascii_lowercase):  # reversed = DFS
                stack.append(prefix + c)

        save_progress(stack)

    print(f"\n🎉 Done! Total unique names: {len(seen_names)}")

if __name__ == "__main__":
    crawl()
