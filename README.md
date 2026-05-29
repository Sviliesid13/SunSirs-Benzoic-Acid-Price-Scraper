[README.md](https://github.com/user-attachments/files/28372436/README.md)
# SunSirs Benzoic Acid Price Scraper

Automated daily scraper for the benzoic acid spot price on [SunSirs](https://www.sunsirs.com/uk/prodetail-177.html).  
Runs on GitHub Actions — **no server, no computer required**.

## How it works

```
GitHub Actions (CRON: daily 09:00 UTC)
  └─> scraper.py  (Playwright headless Chrome)
      └─> Extracts date + price
      └─> Appends row to prices.csv
      └─> Commits & pushes back to this repo
```

## Setup (5 minutes)

1. **Fork or create a new GitHub repo** and push these files.
2. Go to **Settings → Actions → General** and confirm that Actions are enabled.
3. Go to the **Actions** tab and run the workflow manually once (`workflow_dispatch`) to verify it works.
4. That's it — the workflow will run every day at 09:00 UTC automatically.

> **Note:** GitHub Actions free tier provides 2,000 minutes/month for private repos  
> and **unlimited** minutes for public repos. This job takes ~3–5 minutes per run,  
> so you're well within limits either way.

## Output

`prices.csv` is updated daily with a new row:

```
date,price_cny_per_ton
2025-05-28,7200
2025-05-29,7215
...
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Workflow fails with "could not extract price" | Site layout changed — inspect the page and update selectors in `scraper.py` |
| Push step fails with 403 | Go to Settings → Actions → General → set "Workflow permissions" to **Read and write** |
| Bot detection blocks the scraper | Add a longer `wait_for_timeout`, or rotate the user-agent string in `scraper.py` |

## Optional: display on your Cloudflare Pages site

Since `prices.csv` lives in your repo, your Cloudflare Pages build can read it and render a chart.  
A minimal example using Chart.js + PapaParse is in `index.html` (if included).
