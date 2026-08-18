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
