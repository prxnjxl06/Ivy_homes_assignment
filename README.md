# Autocomplete API Name Scraper

## Overview

This project is a technical assignment designed to extract **all possible names** from an undocumented autocomplete API:

```
http://35.200.185.69:8000/v1/autocomplete?query=<prefix>
```

The challenge was to reverse-engineer how the API behaves, work within its rate limits, and collect the **complete list of hidden names**, despite the fact that only **10 results** are returned per query and no documentation is provided.

---

## Problem Understanding

The `/autocomplete` endpoint returns at most **10 matching results** for a given string prefix. The API:

- Is **case-sensitive** (only lowercase queries return results)
- Returns a JSON object:  
  `{ "version": "v1", "count": <int>, "results": [<name1>, <name2>, ...] }`
- Enforces a **rate limit of 100 requests per minute**
- Returns **no names** for symbols, numbers, or uppercase letters

To retrieve **all available names**, a brute force prefix search was inefficient and would miss lower-ranked results. Instead, a **systematic recursive strategy** was required.

---

## Final Approach (That Worked)

We implemented a **lexicographic prefix-based crawler** that behaves like a tree traversal:

### Core Logic:

1. **Start with prefixes `["a" to "z"]`**.
2. For each prefix:
   - Query the API: `/autocomplete?query=<prefix>`
   - If `count < 10`, store all returned names and **do not go deeper**.
   - If `count == 10`, **assume more names exist**, so:
     - Add all 26 possible child prefixes (`prefix + a`, `prefix + b`, ..., `prefix + z`) to the stack for deeper crawling.
3. Use a **stack** (DFS-style traversal) to ensure full tree coverage.
4. Track and store all discovered names in a `.csv` file.
5. Persist crawler state in a `progress.txt` file so it can **resume from any crash or stop point**.

### Summary of Files

| File            | Description |
|-----------------|-------------|
| `name_scraper.py` | Main Python script |
| `all_names.csv`   | Final list of all scraped names |
| `progress.txt`    | Stack of pending prefixes, for resumable crawling |

---

## Results

| Metric                     | Value           |
|----------------------------|-----------------|
| **Total names collected**  | 18,342 ✅        |
| **Max results per query**  | 10              |
| **Rate limit respected**   | 100 requests/minute |
| **Final explored prefix**  | `"zzz"`         |
| **Script resumable**       | Yes (via `progress.txt`) |

---

## How to Run

### Prerequisites

- Python 3.x
- `requests` library:
  ```bash
  pip install requests
  ```

### Run the Scraper

```bash
python name_scraper.py
```

- It will begin from the prefixes in `progress.txt`
- New names are saved to `all_names.csv`
- Automatically waits if rate-limited (HTTP 429)

### Resuming After Interruptions

- To resume, simply re-run:
  ```bash
  python name_scraper.py
  ```
- It will load `progress.txt` and continue where it left off.

###  Resume from a Specific Prefix

Edit `progress.txt` to:
```json
["x"]
```
Or any other prefix from which you want to continue crawling.

---

## Key Challenges & How We Solved Them

| Challenge | Solution |
|----------|----------|
| **Unknown API behavior** | Reverse-engineered via experimentation |
| **Rate-limiting (429 errors)** | Detected and backed off with sleep intervals |
| **Incomplete results (10 max per query)** | Used recursive prefix deepening until leaf |
| **Missing down-ranked names** | Crawled the full prefix tree up to depth of `'zzzzz'` |
| **Resumability** | Saved pending prefixes in a file (`progress.txt`) |
| **Duplicates** | Maintained a Python `set` to filter repeated names |

---

## Observations

- The API returns names in **partial rank order**, so crawling deeper reveals hidden names not surfaced with shorter prefixes.
- The data likely includes both real and synthetic names (random-looking ones too).
- Some names are only exposed with deep prefixes like `"zzx"`, `"zzyy"`, etc.

---

## Possible Enhancements

- Add retry caps and smarter exponential backoff
- Store to SQLite instead of CSV for better querying
- Add test mode with limited prefix depth
- Parallelize prefix crawling across multiple processes/machines (with rate coordination)

---

## Conclusion

This project demonstrates a **systematic and intelligent API crawling approach** under constraints of:
- No documentation
- Strict rate limits
- Hidden data and ranking behavior

By simulating a full prefix tree traversal and backing it with resumable state, we successfully collected **18,342 unique names** from the autocomplete system.
