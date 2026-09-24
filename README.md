# Zenrows vs Browserbase Benchmark

This project benchmarks Zenrows against Browserbase for accessing protected and dynamic web pages.

The benchmark, conducted on the **17th of August 2026**, sends repeated requests to the same five websites using both platforms and measures successful page retrieval, response times, and HTTP status codes.

Zenrows is tested using `mode=auto`, while Browserbase is tested using its default Fetch configuration.

## Features

- Benchmarks Zenrows and Browserbase against the same five targets
- Sends 100 requests per target
- Uses a controlled rate of 2 requests per second
- Tests different types of web pages
- Validates returned pages using expected content
- Records API and target HTTP status codes
- Measures response time for every request
- Calculates success rates
- Saves raw benchmark results as CSV files
- Supports running either platform independently or both platforms

## Prerequisites

Before running the benchmark, make sure you have:

- Python 3.9 or later
- A Zenrows API key
- A Browserbase API key

## Installation

Clone the repository:

```bash
git clone https://github.com/Techwithpraisejames/zenrows-vs-browserbase-benchmark.git
cd zenrows-vs-browserbase-benchmark
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Add your API keys to `.env`:

```env
ZENROWS_API_KEY=your-zenrows-api-key
BROWSERBASE_API_KEY=your-browserbase-api-key
```

The benchmark loads these environment variables when the script runs. The `.env` file is excluded from Git through `.gitignore`, so your API keys are not committed to the repository.

## Project structure

```text
.
├── results
│   ├── browserbase_results.csv
│   ├── summary_browserbase.csv
│   ├── summary_zenrows.csv
│   └── zenrows_results.csv
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run_benchmark.py
```

- `run_benchmark.py` contains the benchmark script.
- `results/zenrows_results.csv` contains the raw Zenrows benchmark results.
- `results/browserbase_results.csv` contains the raw Browserbase benchmark results.
- `results/summary_zenrows.csv` contains the summarized Zenrows benchmark results.
- `results/summary_browserbase.csv` contains the summarized Browserbase benchmark results.
- `.env.example` provides the environment variable names required by the benchmark.
- `.gitignore` excludes local environment files and other files that should not be committed.
- `requirements.txt` lists the dependencies required to run the benchmark.

## How it works

The benchmark uses the same five target pages for both platforms and sends 100 requests to each target at a controlled rate of 2 requests per second.

For each request, the script records:

- Target URL
- Platform
- API HTTP status code
- Target HTTP status code
- Expected content match
- Success status
- Response time
- Timestamp

A request is considered successful when the returned page meets the expected content checks defined for that target.

The benchmark runs Zenrows with `mode=auto` and Browserbase with its default Fetch configuration. Each platform can also be run independently.

## Running the project

Run the benchmark:

```bash
python run_benchmark.py
```

The benchmark can also run either platform independently:

```bash
python run_benchmark.py --tool zenrows
```

```bash
python run_benchmark.py --tool browserbase
```

Or run both platforms:

```bash
python run_benchmark.py --tool both
```

Make sure your Zenrows and Browserbase API keys are configured in `.env` before starting the script.

## Output

The benchmark produces four CSV files in the `results/` directory:

- `zenrows_results.csv` contains request-level results for Zenrows.
- `browserbase_results.csv` contains request-level results for Browserbase.
- `summary_zenrows.csv` contains summarized results for Zenrows.
- `summary_browserbase.csv` contains summarized results for Browserbase.

The raw results can be used to inspect individual requests, HTTP status codes, response times, and success status. The summary files provide aggregated benchmark results for each target.

## Technologies

- Python
- Zenrows Fetch API
- Browserbase Fetch API
- Requests
- Browserbase Python SDK
- CSV

## Related article

This benchmark is part of the blog:

**[Best Browserbase Alternative in 2026 for Protected Web Access](https://www.zenrows.com/blog/best-browserbase-alternative-for-protected-web-access)**
