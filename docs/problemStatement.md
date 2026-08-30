# RAG FOR GROW — PRODUCT REQUIREMENTS / PROBLEM STATEMENT

This document is the complete product requirements specification for the Groww-source-grounded RAG chatbot. It intentionally focuses on product behavior, functional requirements, business rules, user experience, and acceptance criteria. It does not prescribe a specific software architecture or implementation technology.

## PROJECT PROBLEM STATEMENT

### Project Title

Groww Market Intelligence – Source-Grounded RAG Chatbot

### 1. Project Objective

Build a source-grounded Retrieval-Augmented Generation (RAG) chatbot that answers user questions about stocks, mutual funds, New Fund Offers (NFOs), and Groww market-news information using only information collected from the specified Groww website sources.

The chatbot must prioritize factual accuracy, source grounding, data freshness, and strict prevention of hallucinated or advisory responses.

The system should continuously refresh its source data every 15 minutes so that users can ask questions using recently collected information.

### 2. Core User Experience

The application should provide a conversational chatbot interface where a user enters a question in natural language.

Examples of supported questions include:

- What is the current NAV of HDFC Mid Cap Fund?
- What is the expense ratio of HDFC Small Cap Fund?
- What are the 1-year and 3-year returns shown for Nippon India Small Cap Fund?
- What is the risk level of HDFC Defence Fund?
- Which funds in the available dataset belong to the pharma and healthcare theme?
- Compare the available HDFC Small Cap Fund and Nippon India Small Cap Fund information.
- What new fund offerings are currently available?
- What are the latest market-news items available from Groww?
- What changed in the available fund or market information since the previous refresh?

The chatbot should understand natural-language variations, follow-up questions, and requests referring to a previously discussed fund or news item, provided the required information exists in the available source data.

### 3. Mandatory Source Data

The initial source dataset must be collected from the following Groww URLs.

#### Mutual Fund / AMC Sources

- https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth
- https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth
- https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth
- https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
- https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth
- https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth
- https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth
- https://groww.in/mutual-funds/hdfc-transportation-and-logistics-fund-direct-growth
- https://groww.in/mutual-funds/hdfc-large-and-mid-cap-fund-direct-growth
- https://groww.in/mutual-funds/hdfc-nifty-next-50-index-fund-direct-growth
- https://groww.in/mutual-funds/groww-banking-financial-services-fund-direct-growth
- https://groww.in/mutual-funds/groww-nifty-ev-new-age-automotive-etf-fof-direct-growth
- https://groww.in/mutual-funds/groww-nifty-india-defence-etf-fof-direct-growth
- https://groww.in/mutual-funds/groww-multicap-fund-direct-growth
- https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth
- https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth
- https://groww.in/mutual-funds/nippon-india-nifty-midcap-150-index-fund-direct-growth
- https://groww.in/mutual-funds/nippon-india-pharma-fund-direct-growth
- https://groww.in/mutual-funds/amc/aditya-birla-sun-life-mutual-funds
- https://groww.in/mutual-funds/birla-sun-life-manufacturing-equity-fund-direct-growth
- https://groww.in/mutual-funds/aditya-birla-sun-life-psu-equity-fund-direct-growth
- https://groww.in/mutual-funds/aditya-birla-sun-life-nifty-india-defence-index-fund-direct-growth
- https://groww.in/mutual-funds/birla-sun-life-corporate-bond-fund-direct-growth
- https://groww.in/mutual-funds/birla-sun-life-equity-fund-direct-growth
- https://groww.in/mutual-funds/aditya-birla-sun-life-pharma-healthcare-fund-direct-growth
- https://groww.in/mutual-funds/aditya-birla-sun-life-transportation-and-logistics-fund-direct-growth
- https://groww.in/mutual-funds/aditya-birla-sun-life-multi-asset-allocation-fund-direct-growth
- https://groww.in/mutual-funds/franklin-india-small-cap-fund-direct-growth
- https://groww.in/mutual-funds/franklin-india-multi-cap-fund-direct-growth
- https://groww.in/mutual-funds/franklin-india-multi-asset-allocation-fund-direct-growth
- https://groww.in/mutual-funds/filter?fund_house=%5B%22Nippon+India+Mutual+Fund%22%2C%22Aditya+Birla+Sun+Life+Mutual+Fund%22%2C%22Angel+One+Mutual+Fund%22%2C%22Axis+Mutual+Fund%22%2C%22Bajaj+Finserv+Mutual+Fund%22%2C%22Franklin+Templeton+Mutual+Fund%22%2C%22Groww+Mutual+Fund%22%2C%22HDFC+Mutual+Fund%22%2C%22HSBC+Mutual+Fund%22%2C%22ICICI+Prudential+Mutual+Fund%22%2C%22IDFC+Mutual+Fund%22%2C%22IIFL+Mutual+Fund%22%2C%22Kotak+Mahindra+Mutual+Fund%22%2C%22LIC+Mutual+Fund%22%2C%22Motilal+Oswal+Mutual+Fund%22%2C%22Navi+Mutual+Fund%22%2C%22Quantum+Mutual+Fund%22%2C%22SBI+Mutual+Fund%22%2C%22Tata+Mutual+Fund%22%2C%22Zerodha+Mutual+Fund%22%2C%22YES+Mutual+Fund%22%5D

#### Market News Source

- https://groww.in/share-market-today

#### New Fund Offering Source

- https://groww.in/nfo

The NFO and Share Market Today sources are mandatory because they provide additional source-grounded information for the proposed NFO and market-news features.

### 4. Data Freshness Requirement

The specified Groww sources must be refreshed every 15 minutes.

Each refresh should identify and process newly available or changed information and make the latest valid information available to the chatbot.

The system should maintain enough freshness metadata to distinguish current information from older information.

Where a value or statement is time-sensitive, the chatbot should make the relevant source timestamp or last-refresh time visible to the user when appropriate.

The chatbot must never present stale information as though it were freshly collected.

### 5. Information That Should Be Captured

The chatbot should be able to answer questions using factual information exposed by the specified Groww pages, such as applicable:

- Fund name
- AMC / fund house
- Fund category and sub-category
- Scheme type / plan information
- NAV and NAV date, when available
- Historical performance figures shown by the source, such as 1-year, 3-year, 5-year, 7-year, or 10-year returns when available
- Expense ratio
- Exit load
- Risk level / risk indicator
- Fund size / AUM when available
- Ratings shown by the source
- Fund manager information when available
- Portfolio / holdings information when available
- Asset allocation information when available
- Benchmark or index information when available
- Investment objective / scheme description when available
- Other factual fund attributes explicitly present on the source page

For the AMC page, the chatbot may answer factual questions using information explicitly present on that AMC source page.

For the Share Market Today source, the chatbot should be able to answer using the market-news information actually collected from that page, including available article titles, dates/times, summaries or descriptions, and other factual metadata present in the source.

For the NFO source, the chatbot should be able to answer using available NFO information such as fund name, AMC, subscription status or dates, offer-related facts, category, and other factual fields actually present in the source at the time of collection.

### 6. Strict RAG Grounding Rules

The chatbot is strictly source-grounded.

- Every answer must be generated only from information retrieved from the processed Groww source data.

- The model must NOT use its general world knowledge to fill gaps in the retrieved information.

- The model must NOT invent values, dates, returns, fund characteristics, news details, NFO details, or relationships that are not supported by the stored source data.

- The model must NOT infer a fact when the inference could introduce unsupported financial information.

- When the retrieved source data does not contain enough information to answer the user's question, the chatbot must return exactly:

  > "Currently I dont have the data to answer the query"

- The same fallback must be used when the requested entity, metric, date, news item, or NFO information is not present in the available dataset.

### 7. No Investment Advice – Mandatory Restriction

The chatbot must strictly provide information and factual comparisons only.

It must NOT provide:

- Investment advice
- Buy / sell / hold recommendations
- Personalized investment recommendations
- Portfolio recommendations
- Predictions of future returns or prices
- Statements claiming that a fund or stock is guaranteed to perform well
- Risk-taking instructions
- Timing recommendations such as "buy now" or "wait"
- Personalized financial planning
- Tax advice
- Any other advisory or decision-making recommendation

If a user asks for advice, the chatbot should not provide advice. It should respond using the same source-availability rule and remain factual and informational.

### 8. Query Types the Chatbot Should Support

The chatbot should support factual natural-language queries covering:

- Single-fund information lookup
- Single-stock or market-news information lookup when supported by the collected source data
- Fund-to-fund comparisons
- Multiple-fund comparisons
- Metric-specific questions
- Category-based questions
- AMC-based questions
- Theme-based questions when the theme is explicitly represented in the source data
- Historical performance questions when the requested historical metric exists in the scraped data
- News lookup and summarization strictly from collected Groww market-news content
- NFO discovery and factual NFO status/details lookup
- Follow-up questions that refer to entities already established in the conversation
- Questions about data freshness, such as when the information was last refreshed

### 9. Comparison Capability

The chatbot should be capable of producing factual side-by-side comparisons when sufficient data exists for all requested entities.

For example, when asked to compare two or more mutual funds, the response may compare available factual fields such as:

- NAV
- Returns
- Expense ratio
- Risk
- Fund size / AUM
- Rating
- Exit load
- Category
- Benchmark
- Other fields explicitly available in the source data

The chatbot must not convert a factual comparison into a recommendation or declare a winner unless the user's question can be answered purely as a factual statement from the source data.

### 10. Source Traceability and Transparency

Every substantive chatbot response should make it clear that the answer is based on Groww-sourced data.

Where practical, the response should identify the source page, source type, and the latest available collection/refresh time associated with the information used to answer the question.

The user should be able to distinguish information coming from:

- Mutual fund pages
- AMC pages
- NFO page
- Share Market Today page

The chatbot should not claim that it has access to information outside these configured source datasets.

### 11. Data Freshness and Change Awareness

The application should make freshness useful to the user rather than treating scraping as an invisible background process.

A user should be able to ask questions such as:

- When was this fund information last updated?
- Has this fund's available data changed since the previous refresh?
- What new information was detected in the latest refresh?

Where the collected data supports it, the chatbot may summarize factual changes between refreshes, such as a changed NAV, updated performance metric, newly published article, or newly listed NFO.

Any reported change must come directly from the stored source snapshots/history.

### 12. New Feature: New Fund Offering Notifications

Add an NFO discovery and notification capability using: `https://groww.in/nfo`

The application should detect newly appearing NFOs and meaningful changes to existing NFO information during the periodic refresh process.

The feature should support:

- Showing currently available NFOs
- Showing newly detected NFOs
- Showing NFO subscription start/end information when available
- Showing the AMC and fund/category details available from the source
- Highlighting newly detected NFOs since the previous refresh
- Optional user-configurable notifications for newly detected NFOs
- Avoiding duplicate notifications for the same NFO unless meaningful source information changes

NFO notifications must remain informational. They must never say or imply that a user should subscribe to an NFO.

### 13. New Feature: Groww Share Market News Feed

Add a market-news capability using: `https://groww.in/share-market-today`

The application should periodically collect the available market-news content and make it searchable through the same chatbot.

The feature should support:

- Latest available market-news discovery
- Search by topic or company when that information exists in the collected news content
- News summaries strictly based on the retrieved Groww content
- Displaying article title and available publication/update time
- Showing the latest newly detected news items
- Identifying what news was added since the previous refresh
- Optional user notifications for newly detected relevant market-news items

News summaries must not add external facts that are absent from the collected source content.

### 14. New Feature: Ask About Changes Since Last Refresh

Provide a conversational capability to identify factual changes between the current and previous collected versions of the data.

Example questions:

- What changed in HDFC Mid Cap Fund since the last update?
- Which new NFOs appeared in the latest refresh?
- What new market-news articles were detected?

Only actual detected changes should be reported.

### 15. New Feature: Fund Comparison Workspace

Provide a convenient way for users to compare selected funds in a structured factual view.

The comparison workspace should allow users to select multiple funds and display common available metrics side by side.

Missing values should be shown as unavailable rather than guessed or calculated from unsupported information.

The workspace must remain informational and must not rank or recommend funds unless the ranking is explicitly based on a user-selected factual metric and the displayed result clearly remains a factual calculation over the available dataset.

### 16. New Feature: Natural-Language Market Discovery

Allow users to ask discovery-style questions over the available source data, such as:

- Show funds related to defence that are present in the dataset.
- Which available funds have the lowest expense ratio?
- Which available funds have a 5-year return value in the collected data?
- Show the latest NFOs.
- Show the latest market-news items.

Results must be calculated only from the collected dataset and must never silently expand the scope to external information.

### 17. New Feature: User Watchlist / Saved Topics

Allow a user to save funds, AMC pages, NFO topics, or market-news topics they are interested in.

The application may then provide a consolidated view of:

- Latest available information
- Detected changes
- Newly available NFOs
- Relevant newly collected market-news items

This feature must remain informational and must not issue investment recommendations.

### 18. New Feature: Data Availability Indicator

The user interface should clearly show the availability state of the data used by the chatbot.

For example, the application should distinguish between:

- Data available and recently refreshed
- Data available but older than the most recent refresh cycle
- Source temporarily unavailable
- No usable data available for the requested entity

The interface should avoid presenting a partially failed refresh as though all source data were current.

### 19. New Feature: Source-Only Answer Mode

Provide a clearly visible mode or indicator showing that the chatbot is operating in "Groww Source-Only" mode.

This should reinforce the core product promise that responses are generated only from the configured Groww data sources.

### 20. Conversation Behavior

The chatbot should behave naturally while preserving strict grounding.

It should:

- Understand follow-up questions.
- Resolve references such as "this fund" or "the second one" using conversation context when the referenced entity is unambiguous.
- Ask for clarification when a user query is ambiguous and multiple entities could match, rather than inventing an interpretation.
- Preserve factual context within a conversation.
- Refuse to manufacture missing information.
- Use the exact fallback response when the required information is unavailable.

### 21. Handling Missing, Conflicting, or Stale Information

If the source data does not contain a requested field, the chatbot must not guess.

If multiple source records conflict, the chatbot should not silently select an arbitrary value. It should either use the clearly latest valid source record according to the collected source metadata or state that the information is unavailable/unclear based on the available source data.

If a page cannot be collected during a refresh, previously valid data should not be falsely presented as newly refreshed data.

### 22. Accuracy Requirements

The primary success criterion is factual faithfulness to the collected Groww data.

The chatbot should prioritize:

1. Correct retrieval of the relevant source information.
2. Correct interpretation of the user query.
3. Accurate generation using only retrieved information.
4. Clear indication of missing information.
5. Zero unsupported financial claims.
6. Zero investment advice.

A confident answer that is not supported by the source data must be treated as a failure.

### 23. User Experience Requirements

The chatbot interface should feel like a modern financial information assistant while making the source-grounding restriction obvious.

The UI should include, as appropriate:

- Chat conversation area
- User query input
- Clear response area
- Source/freshness indication
- Last refreshed time
- Data availability status
- Structured comparison views for comparison questions
- NFO discovery section
- Market-news section
- Optional notification settings
- Watchlist/saved-topic section

The UI should make informational answers easy to scan without visually implying that the application is providing financial advice.

### 24. Explicit Non-Goals

The product must NOT become:

- An investment advisor
- A stock-picking engine
- A portfolio recommendation engine
- A financial planning assistant
- A prediction engine for future stock prices or fund returns
- A general-purpose chatbot that answers questions from its own pretrained knowledge
- A web search engine for arbitrary external websites

The product scope is limited to source-grounded factual information derived from the configured Groww data sources.

### 25. Primary Acceptance Criteria

The finished chatbot should satisfy all of the following conditions:

- It accepts natural-language user questions.
- It answers using the configured Groww source dataset.
- The Groww source pages are refreshed every 15 minutes.
- The specified mutual-fund and AMC URLs are included as mandatory initial sources.
- Groww Share Market Today is included as the market-news source.
- Groww NFO is included as the NFO source.
- Answers are strictly grounded in available collected source data.
- The chatbot never knowingly hallucinates missing financial information.
- The exact fallback message is used when the required information is unavailable: "Currently I dont have the data to answer the query"
- The chatbot does not provide investment advice or recommendations.
- Factual comparisons are supported when sufficient data exists.
- Source and freshness information can be shown to the user.
- Newly detected NFOs can be surfaced and optionally notified.
- Newly detected market-news items can be surfaced and optionally notified.
- Users can ask about changes since the last refresh when historical refresh data supports the request.
- Missing fields remain missing rather than being inferred or fabricated.
- The chatbot remains informational even when the user explicitly asks for an investment recommendation.

### 26. Overall Product Goal

Create a trustworthy, continuously refreshed, Groww-source-only RAG chatbot that acts as a factual information layer over the configured mutual-fund, AMC, NFO, and market-news content.

The defining product principles are:

- **SOURCE-GROUNDED**: Every substantive answer must be supported by the collected Groww data.
- **FRESH**: The configured sources are refreshed every 15 minutes and freshness is visible where relevant.
- **NO HALLUCINATION**: Missing information must never be invented.
- **NO ADVICE**: The chatbot provides facts and comparisons, not investment recommendations or financial advice.
- **TRANSPARENT**: Users can understand what source information and freshness context support an answer.
- **USEFUL**: Users can search, compare, discover changes, follow NFOs, and stay informed about Groww market-news content through a single conversational interface.

---

## MANDATORY REQUIREMENTS SUMMARY — DO NOT OMIT

### A. ADMIN FEATURE — MANDATORY

1. Normal chatbot users must NOT be required to log in.
2. A dedicated Admin Login page must exist.
3. Initial administrator credentials for the requested project setup:
   - **Username:** `admin`
   - **Password:** `admin`
4. Only authenticated administrators may access the Admin area.
5. The Admin area must allow an administrator to:
   - View all currently configured scraping URLs.
   - Add a new scraping URL.
   - Delete an existing scraping URL.
   - Save the updated URL configuration.
   - Manually trigger the scheduler/refresh after saving configuration changes.
   - View overall refresh status.
   - View source-level refresh status.
   - View last successful refresh time.
   - View the latest refresh attempt time.
   - View scraping/processing errors for individual sources.
6. The configured URL list is the authoritative set of sources that should participate in future scraping/refresh cycles.
7. After an administrator saves URL changes and triggers synchronization:
   - Deleted URL data must be removed from the active vector database.
   - Newly added URLs must be scraped and, after successful collection, their processed data must be added to the vector database.
   - Existing URLs must be checked for changes.
   - Existing URLs with unchanged content must retain their current vectors and must not be unnecessarily re-embedded.
   - Existing URLs with changed content must have their active data reconciled/replaced with the newly successful scrape.
8. The active knowledge base after a successful synchronization must match the current administrator-configured source URL set.

### B. SCRAPING FAILURE HANDLING — MANDATORY

1. Scraping is attempted every 15 minutes for all currently configured URLs.
2. The refresh process must be incremental and source-aware.
3. If a source fails to scrape because of a temporary website problem, network failure, timeout, parsing problem, or other collection failure:
   - The previously successful data for that source must NOT be deleted.
   - The previously successful data must remain available to the chatbot.
   - The source must be marked as failed/stale/unavailable for the latest attempt.
   - The failure must be recorded for administrator visibility.
4. The system must distinguish between:
   - Last attempted refresh time.
   - Last successful refresh time.
   - Current refresh status.
5. A failed scrape must never be reported as a successful refresh.
6. A temporarily failed source must not cause the entire vector database to be deleted or rebuilt.
7. When a later scrape for the failed source succeeds, the newer successful content must replace/reconcile the previously retained version.
8. The chatbot must not present a failed refresh as though it contains newly collected data.

### C. 15-MINUTE VECTOR DATABASE SYNCHRONIZATION — MANDATORY

Every scheduled cycle must follow this source-level behavior:

- **UNCHANGED SOURCE**: Keep existing active vectors; do not unnecessarily re-embed.
- **CHANGED SOURCE**: Replace/reconcile only that source's active vectors with the new successfully scraped content.
- **NEW SOURCE**: Scrape, process, embed, and add the newly collected source content.
- **DELETED SOURCE**: Remove the deleted source's active vectors from the knowledge base.
- **FAILED SOURCE**: Retain the last successfully scraped active vectors and record the failure; do not delete valid prior data.

The same synchronization rules apply to:

- The automatic 15-minute scheduler.
- The administrator-triggered scheduler after URL configuration changes.

### D. SOURCE-GROUNDED CHATBOT BEHAVIOR — MANDATORY

1. Answers must come only from the successfully collected and currently active Groww source data.

2. The chatbot must not use general model knowledge to fill missing facts.

3. The chatbot must not hallucinate values, dates, returns, prices, fund characteristics, news details, NFO details, or unsupported comparisons.

4. When the requested information is not available in the collected source data, the chatbot must return exactly:

   > "Currently I dont have the data to answer the query"

5. The chatbot must never provide investment advice, buy/sell/hold recommendations, personalized financial advice, portfolio advice, predictions, or timing recommendations.

### E. USER / ADMIN ACCESS BOUNDARY — MANDATORY

- **NORMAL USER**:
  - No login required.
  - Can use the normal chatbot experience.
- **ADMIN**:
  - Must authenticate through the dedicated Admin Login page.
  - Can manage scraping URLs and trigger refresh/synchronization.
  - Can view operational refresh status and scraping failures.

Administrative controls must never be exposed as normal chatbot controls.