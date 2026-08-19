# Zenrows vs Browserbase Benchmark

This project benchmarks Zenrows against Browserbase for accessing protected and dynamic web pages.

The benchmark sends repeated requests to the same five websites using both platforms and measures successful page retrieval, response times, and HTTP status codes.

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
- Internet access

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd <your-repository-directory>

## Configuration

Set the API keys for both platforms before running the benchmark.

The benchmark expects the following environment variables:

```bash
export ZENROWS_API_KEY="your-zenrows-api-key"
export BROWSERBASE_API_KEY="your-browserbase-api-key"
```

On Windows PowerShell:

```powershell
$env:ZENROWS_API_KEY="your-zenrows-api-key"
$env:BROWSERBASE_API_KEY="your-browserbase-api-key"
```

## Project structure

```text
.
├── run_benchmark.py
├── zenrows_results.csv
├── browserbase_results.csv
└── requirements.txt
```

- `run_benchmark.py` contains the benchmark script.
- `zenrows_results.csv` contains the raw Zenrows benchmark results.
- `browserbase_results.csv` contains the raw Browserbase benchmark results.
- `requirements.txt` lists the Python dependencies required to run the benchmark.

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

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the benchmark:

```bash
python run_benchmark.py
```

Make sure the required API keys are available as environment variables before starting the script.

The benchmark writes the raw results to separate CSV files for Zenrows and Browserbase.

## Output

The benchmark produces four CSV files. Each file contains the request-level results from the corresponding platform. These files can be used to calculate success rates, compare response times, inspect HTTP status codes, and analyze individual requests.

## Technologies

- Python
- Zenrows Fetch API
- Browserbase Fetch API
- Requests
- Browserbase Python SDK
- CSV

## Related article

This benchmark is part of the blog:

**Best Browserbase Alternative in 2026 for Protected Web Access**
