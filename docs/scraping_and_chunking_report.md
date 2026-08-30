# Mutual Fund Scraping & Chunking Strategy Report

## 1. Scraping & Normalization Implementation
I have implemented the extraction logic for Groww mutual fund pages. The Groww pages are built with Next.js and store all structured data within the `__NEXT_DATA__` script tag.

I updated `backend/app/scraper/extractors/mutual_fund.py` to parse this embedded JSON (`mfServerSideData`), which is much more robust than scraping the DOM elements.

## 2. Processed Data Analysis
Using the `https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth` URL, the newly implemented extractor generated the following rich, normalized dataset:

```json
{
  "fund_name": "HDFC Mid Cap Fund Direct Growth",
  "nav": "237.124",
  "nav_date": "24-Aug-2026",
  "returns_1y": "10.72",
  "returns_3y": "19.34",
  "returns_5y": "21.33",
  "expense_ratio": "0.74",
  "exit_load": "Exit load of 1% if redeemed within 1 year.",
  "risk_level": 5,
  "fund_size_aum": "105142.6943",
  "rating": "5",
  "fund_manager": "Chirag Setalvad",
  "category": "Equity",
  "amc": "HDFC",
  "top_holdings": [
    { "company": "Repo", "percentage": 8.11 },
    { "company": "The Federal Bank Ltd", "percentage": 4.18 }
    // ... up to top 10
  ]
}
```

**Observations on the Data:**
- **Highly Structured:** The data is a collection of key-value pairs rather than unstructured narrative text.
- **Compact Size:** The entire JSON for a single mutual fund is quite small (~1.5 KB or ~300-400 tokens).

## 3. Recommended Chunking Strategy

Since this is structured entity data, traditional NLP chunking (e.g., fixed-size sliding windows or recursive character splitting) will destroy the semantic relationships between the fund's name and its attributes.

Based on the data profile, here are the best strategies:

### Primary Recommendation: Single-Document Textification
Given that the total token count per fund is well under typical embedding model limits (e.g., 512 or 8192 tokens), **you should not chunk this data at all.**

Instead, use a **Textification Strategy**: Convert the JSON into a single, comprehensive Markdown document (or natural language summary) before passing it to the embedding model. This keeps all context bound together.

**Example Textified Output (Single Chunk):**
> **HDFC Mid Cap Fund Direct Growth** is an Equity mutual fund managed by HDFC AMC and fund manager Chirag Setalvad. It has a fund size (AUM) of ₹105,142 Cr and a risk rating of 5.
> **Performance:** The 1-year return is 10.72%, 3-year return is 19.34%, and 5-year return is 21.33%.
> **Costs & NAV:** The current NAV is 237.124 (as of 24-Aug-2026), with an expense ratio of 0.74%. The exit load is 1% if redeemed within 1 year.
> **Top Holdings:** The top holdings include Repo (8.11%), The Federal Bank Ltd (4.18%), etc.

### Alternative: Semantic Section Chunking (If context window is strictly limited)
If you must split the data (e.g., to reduce prompt payload size or increase vector search specificity), split it logically by sections, ensuring the `fund_name` is injected into every chunk as metadata:

- **Chunk 1 (Metadata & Costs):** Fund Name, AMC, Category, Manager, AUM, NAV, Expense Ratio, Exit Load.
- **Chunk 2 (Performance):** Fund Name, 1Y, 3Y, 5Y returns, Risk rating.
- **Chunk 3 (Portfolio):** Fund Name, Top 10 Holdings, Sector allocation.

> [!TIP]
> **Conclusion:** I strongly recommend the **Single-Document Textification** approach. It prevents "attribute leakage" where an LLM might mix up the expense ratio of Fund A with Fund B because they were chunked separately, and ensures maximum context retrieval for RAG.
