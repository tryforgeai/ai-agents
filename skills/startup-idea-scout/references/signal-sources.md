# Free signal sources (read in step 2 every run)

Use web_fetch / WebSearch for every request. Do not fetch with curl or Python. If a domain is blocked (e.g. reddit.com), do not try to reach it another way; use WebSearch results about it instead.

**Why this order matters.** Developer communities (Hacker News, GitHub) mostly surface developers' own problems: agent tooling, evals, security, memory. That layer is the most crowded in AI, so a run that relies on it will "find" a red ocean every time. Pain signals must come mainly from **the industry itself**: the people who do the work, the companies that pay for it, and the rules that change it. Developer sources are for capability signals (why now), not for pain.

**Source-mix rule:** at least half of the pain signals must come from sections A–D below. Hacker News and GitHub can supply at most half of the pain signals; the script warns when they supply more.

## Timestamps: compute them, do not do mental math

```bash
python3 -c "import time; print(int(time.time()) - 60*86400)"   # unix timestamp 60 days ago
```

## A. Where companies admit spend and pain: SEC filings (US public companies)

Full-text search over 10-K / 10-Q filings, free, no key:

```
https://efts.sec.gov/LATEST/search-index?q=%22<phrase>%22&forms=10-K&dateRange=custom&startdt=<YYYY-MM-DD>&enddt=<YYYY-MM-DD>
```

Useful phrases: "manual processes", "manual reconciliation", "material weakness", "labor shortage", "claims processing costs", "chargebacks", "customer acquisition cost". Results list companies and filing IDs (`adsh`, `ciks`); a filing opens at `https://www.sec.gov/Archives/edgar/data/<cik>/<adsh-without-dashes>/<filename>`. The response is large: Grep for `"display_names"`, `"file_date"`, `"sics"`. A phrase that shows up in many filings of one industry (SIC code) is a strong buyer-and-budget signal.

## B. What changes the rules: Federal Register (US regulation)

```
https://www.federalregister.gov/api/v1/documents.json?per_page=10&order=newest&conditions[term]=<words>&conditions[type][]=RULE
```

New rules create compliance work that nobody has software for yet. Use specific terms (e.g. "recordkeeping", "disclosure", "reporting requirement" plus an industry word); generic terms return noise. Filter `conditions[type][]` to RULE or PRORULE.

## C. What work is still done by hand: job postings and operator forums (via WebSearch)

- Job postings: WebSearch for roles that exist only because a process is manual, e.g. "<industry> claims processor job", "accounts receivable specialist <industry> remote", "chargeback analyst". Many open roles for the same manual task = headcount budget a product could replace.
- Operator forums and communities: WebSearch "<industry> forum <problem>", "<job title> biggest headache", "site:reddit.com <industry> <problem>" (read the search results; reddit.com itself is blocked for fetch).
- Trade press and associations: "<industry> association survey 2026 <problem>".

## D. What customers of incumbents complain about: software reviews and switching

WebSearch "<incumbent software> reviews complaints", "<incumbent> alternative for <industry>", "switched from <incumbent>". Persistent complaints about the market leader in a non-software industry are a wedge.

## E. Capability signals (why now): arXiv, Hacker News, GitHub

- **arXiv**: `https://arxiv.org/list/cs.AI/new`, `cs.CL/new`, `cs.LG/new`. The pages are large and get saved to a file: Grep for `Title:` lines and `arXiv:` IDs, then open `https://arxiv.org/abs/<id>`.
- **Hacker News** (also fine for launches and funding chatter):

  ```
  https://hn.algolia.com/api/v1/search?query=<term>&tags=story&numericFilters=created_at_i><timestamp>,points>30&hitsPerPage=15&attributesToRetrieve=title,url,points,objectID,created_at
  https://hn.algolia.com/api/v1/search?query=<term>&tags=comment&numericFilters=created_at_i><timestamp>&hitsPerPage=15&attributesToRetrieve=comment_text,story_title,objectID,created_at
  https://hn.algolia.com/api/v1/items/<objectID>
  ```
  Story link: `https://news.ycombinator.com/item?id=<objectID>`
- **GitHub** (what builders ship): `https://api.github.com/search/repositories?q=<term>+created:><YYYY-MM-DD>&sort=stars&order=desc&per_page=15`; the result is saved to a file, Grep for `"full_name"`, `"description"`, `"stargazers_count"`.

## F. Funding and competitors

WebSearch in standard mode first; send several searches in the same turn.
- Funding: "<industry> AI startup raises 2026"
- Competitors: "<idea> startup", "<idea> alternative", "<incumbent> AI feature"
- Crowding: YC directory `https://www.ycombinator.com/companies/industry/<industry>`

## Known pitfalls

- web_fetch has a URL length limit: keep queries to 1–3 terms and drop optional parameters.
- Algolia multi-term queries require every term to match; more terms means fewer results.
- The Hugging Face papers page may be a stale cache; use arXiv for capability signals.
- Vendor pages are often 30,000+ characters, mostly navigation; read the meta description first.
- For numbers in secondhand coverage, go back to the press release, filing or original report.
- SEC full-text search ignores dates unless both `startdt` and `enddt` are given.

## Signal quality (three criteria for choosing what to observe)

| Criterion | Question | Example |
|---|---|---|
| Validity | Does this signal show someone pays for the problem today? | A 10-K naming the cost, or 30 open roles for the manual task > "this idea is cool" |
| Gain | Are small problems visible? | Complaints with specific workflows, amounts, frequencies > generic trend pieces |
| Lead | Do you learn it early or after the fact? | New rules, operator complaints = leading; funding news = lagging |
