# Tutorial Template: Two Docker Approaches

- This directory provides two versions of the same tutorial setup to help you
  work with Jupyter notebooks and Python scripts inside Docker environments

- Both versions run the same code but use different Docker approaches, with
  different level of complexity and maintainability

## 1. `data605_style` (Simple Docker Environment)

- This version is modeled after the setup used in DATA605 tutorials
- This template provides a ready-to-run environment, including scripts to build,
  run, and clean the Docker container.

- For your specific project, you should:
  - Modify the Dockerfile to add project-specific dependencies
  - Update bash/scripts accordingly
  - Expose additional ports if your project requires them

## 2. `causify_style` (Causify AI dev-system)

- This setup reflects the approach commonly used in Causify AI dev-system
- **Recommended** for students familiar with Docker or those wishing to explore a
  production-like setup
- Pros
  - Docker layer written in Python to make it easy to extend and test
  - Less redundant since code is factored out
  - Used for real-world development, production workflows
  - Used for all internships, RA / TA, full-time at UMD DATA605 / MSML610 /
    Causify 
- Cons
  - It is more complex to use and configure
  - More dependencies from the 
- For thin environment setup instructions, refer to:  
  [How to Set Up Development on Laptop](https://github.com/causify-ai/helpers/blob/master/docs/onboarding/intern.set_up_development_on_laptop.how_to_guide.md)

## Reference Tutorials

- The `tutorial_github` example has been implemented in both environments for you
  to refer to:
  - `tutorial_github_data605_style` uses the simpler DATA605 approach
  - `tutorial_github_causify_style` uses the more complex Causify approach

- Choose the approach that best fits your comfort level and project needs. Both
  are valid depending on your use case.

---

## data source choosing

Those two rows really are for the same asset (the original Bitcoin, ticker BTC-USD on Yahoo and ID bitcoin on CoinGecko), but they come from very different pipelines—so it’s normal to see discrepancies. Here are the main reasons:
	1.	Different data sources & exchange coverage
	•	CoinGecko aggregates trades from dozens of spot exchanges, then computes daily open/high/low/close from that combined feed.
	•	Yahoo Finance feeds (via yfinance.download("BTC-USD")) often draw from a specific subset of venues (and may even include derivative markets), so you’re not seeing the full global volume.
	2.	Time‐stamp & time-zone alignment
	•	CoinGecko’s daily bars are aligned to 00:00 UTC (so “2025-02-05” really means the 24 hours from 00:00 UTC on the 5th to 00:00 UTC on the 6th).
	•	Yahoo Finance will often use the local market close (for crypto it can actually default to UTC nevertheless, but the sample time can differ slightly), so your “open” price may be the last trade on Feb 4 at 23:59 UTC rather than the first Feb 5 price at 00:00 UTC.
	3.	Definition of “volume”
	•	CoinGecko’s total_volume is the USD-value of all spot trades on all exchanges over the 24 hours.
	•	Yahoo’s Volume column for crypto also reports a USD figure but only across its data partners—which can be a different subset of venues.
	4.	No merge bug—just apples vs. oranges
We did in fact pull BTC in both scripts (CoinGecko’s ID was hard-coded to "bitcoin", and yfinance downloaded "BTC-USD"), so there’s no accidental “other coin” slipping in. The difference you’re seeing is simply because the two services measure and timestamp their daily bars differently.

--

## Entrypoint

Run ```./scripts/run_instant.sh``` or ```./scripts/run_history.sh``` to kick off each pipeline.

	•	Load raw CSVs
	•	Resample/aggregate into features
	•	Fit probabilistic STS models
	•	Forecast with uncertainty
	•	Log each step
	•	Configure via a single YAML

---

## Docker

```bash
docker stop bitcoin-forecast-app && docker rm bitcoin-forecast-app && docker rmi docker_causify_style-bitcoin-forecast:latest
```

```bash
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f
```
