import asyncio
import argparse
import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()


# config
REQUESTS_PER_TARGET = 100
CONCURRENCY = 2
RATE_PER_SECOND = 2.0

ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY", "")
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY", "")



# targets
TARGETS = [
    {
        "name": "IKEA product page",
        "url": "https://www.ikea.com/us/en/p/kallax-shelf-unit-white-80275887/",
    },
    {
        "name": "TripAdvisor Paris restaurant listings",
        "url": "https://www.tripadvisor.com/Restaurants-g187147-Paris_Ile_de_France.html",
    },
    {
        "name": "Walmart AirPod product page",
        "url": "https://www.walmart.com/ip/AirPods-Pro-2nd-generation-with-MagSafe-Case-USB-C/5689919121",
    },
    {
        "name": "Amazon search results",
        "url": "https://www.amazon.com/s?k=wireless+mechanical+keyboard",
    },
    {
        "name": "Python documentation",
        "url": "https://docs.python.org/3/",
    },
]


# expected content
EXPECTED_CONTENT = {
    "IKEA product page": [
        "KALLAX",
        "shelf unit"
    ],
    "TripAdvisor Paris restaurant listings": [
        "Restaurants in Paris",
        "Top restaurants in Paris",
    ],
    "Walmart AirPod product page": [
        "AirPods Pro",
    ],
    "Amazon search results": [
        "wireless mechanical keyboard",
    ],
    "Python documentation": [
        "Python",
        "Documentation",
    ],
}


def extract_title(html: str) -> str:
    """Extract the HTML page title."""

    if not html:
        return ""

    try:
        soup = BeautifulSoup(html, "lxml")
        tag = soup.find("title")
        return tag.get_text(strip=True) if tag else ""
    except Exception:
        return ""


def has_expected_content(
    target_name: str,
    html: str,
) -> bool:
    """
    Check whether the returned page contains
    the expected content for the target.
    """

    if not html:
        return False

    expected = EXPECTED_CONTENT.get(target_name)

    if not expected:
        return False

    content = html.lower()

    return all(
        phrase.lower() in content
        for phrase in expected
    )


def ensure_results_dir():
    Path("results").mkdir(exist_ok=True)


def now_ts() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


# rate limiter
class TokenBucket:

    def __init__(self, rate: float):
        self.rate = rate
        self.tokens = rate
        self.last = time.monotonic()

    async def acquire(self):

        while True:

            now = time.monotonic()

            self.tokens += (
                now - self.last
            ) * self.rate

            self.last = now

            if self.tokens > self.rate:
                self.tokens = self.rate

            if self.tokens >= 1:
                self.tokens -= 1
                return

            await asyncio.sleep(0.05)


# zenrows
# fetch with mode=auto
async def zenrows_request(
    session: aiohttp.ClientSession,
    target: dict,
    semaphore: asyncio.Semaphore,
) -> dict:

    params = {
        "apikey": ZENROWS_API_KEY,
        "url": target["url"],
        "mode": "auto",
    }

    async with semaphore:

        start = time.monotonic()

        api_status = 0
        html = ""
        error = ""

        try:

            async with session.get(
                "https://api.zenrows.com/v1/",
                params=params,
                timeout=aiohttp.ClientTimeout(total=90),
            ) as resp:

                api_status = resp.status

                if api_status == 200:

                    html = await resp.text()

                else:

                    error = (
                        await resp.text()
                    )[:1000]

                    print(
                        f"\nZENROWS API ERROR "
                        f"[{target['name']}]"
                    )
                    print(
                        f"HTTP {api_status}: "
                        f"{error}\n"
                    )

        except Exception as exc:

            error = str(exc)

            print(
                f"\nZENROWS REQUEST ERROR "
                f"[{target['name']}]"
            )
            print(
                f"{type(exc).__name__}: "
                f"{exc}\n"
            )

        response_ms = round(
            (time.monotonic() - start) * 1000
        )

    title = extract_title(html)

    expected_content = has_expected_content(
        target["name"],
        html,
    )

    success = (
        api_status == 200
        and bool(title)
        and expected_content
    )

    return {
        "tool": "zenrows",
        "target": target["name"],
        "url": target["url"],
        "api_status_code": api_status,
        "target_status_code": 200 if api_status == 200 else 0,
        "response_ms": response_ms,
        "has_title": bool(title),
        "has_expected_content": expected_content,
        "title": title,
        "content_type": "",
        "success": success,
        "error": error,
    }


# browserbase
# fetch api with default settings
async def browserbase_request(
    session: aiohttp.ClientSession,
    target: dict,
    semaphore: asyncio.Semaphore,
) -> dict:

    headers = {
        "Content-Type": "application/json",
        "X-BB-API-Key": BROWSERBASE_API_KEY,
    }

    payload = {
        "url": target["url"],
    }

    async with semaphore:

        start = time.monotonic()

        api_status = 0
        target_status = 0
        html = ""
        content_type = ""
        error = ""

        try:

            async with session.post(
                "https://api.browserbase.com/v1/fetch",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90),
            ) as resp:

                api_status = resp.status

                if api_status == 200:

                    data = await resp.json()

                    target_status = data.get(
                        "statusCode",
                        0,
                    )

                    html = data.get(
                        "content",
                        "",
                    )

                    content_type = data.get(
                        "contentType",
                        "",
                    )

                else:

                    error = (
                        await resp.text()
                    )[:1000]

                    print(
                        f"\nBROWSERBASE API ERROR "
                        f"[{target['name']}]"
                    )
                    print(
                        f"HTTP {api_status}: "
                        f"{error}\n"
                    )

        except Exception as exc:

            error = str(exc)

            print(
                f"\nBROWSERBASE REQUEST ERROR "
                f"[{target['name']}]"
            )
            print(
                f"{type(exc).__name__}: "
                f"{exc}\n"
            )

        response_ms = round(
            (time.monotonic() - start) * 1000
        )

    title = extract_title(html)

    expected_content = has_expected_content(
        target["name"],
        html,
    )

    success = (
        api_status == 200
        and target_status == 200
        and bool(title)
        and expected_content
    )

    return {
        "tool": "browserbase",
        "target": target["name"],
        "url": target["url"],
        "api_status_code": api_status,
        "target_status_code": target_status,
        "response_ms": response_ms,
        "has_title": bool(title),
        "has_expected_content": expected_content,
        "title": title,
        "content_type": content_type,
        "success": success,
        "error": error,
    }


# runner
async def run_tool(
    tool: str,
    targets: list[dict],
) -> list[dict]:

    semaphore = asyncio.Semaphore(
        CONCURRENCY
    )

    bucket = TokenBucket(
        RATE_PER_SECOND
    )

    all_results = []

    async with aiohttp.ClientSession() as session:

        for target in targets:

            print(
                f"\n[{tool.upper()}] "
                f"{target['name']}"
            )

            async def task(
                i,
                t=target,
            ):

                await bucket.acquire()

                if tool == "zenrows":

                    result = await zenrows_request(
                        session,
                        t,
                        semaphore,
                    )

                else:

                    result = await browserbase_request(
                        session,
                        t,
                        semaphore,
                    )

                if i % 10 == 0 or i == 1:

                    mark = (
                        "OK"
                        if result["success"]
                        else "FAIL"
                    )

                    print(
                        f"  [{i}/"
                        f"{REQUESTS_PER_TARGET}] "
                        f"{mark} "
                        f"{result['response_ms']}ms "
                        f"status="
                        f"{result['target_status_code']}"
                    )

                return result

            results = await asyncio.gather(
                *[
                    task(i + 1)
                    for i in range(
                        REQUESTS_PER_TARGET
                    )
                ]
            )

            successful = sum(
                1
                for result in results
                if result["success"]
            )

            print(
                f"  Done - "
                f"{successful}/"
                f"{REQUESTS_PER_TARGET} "
                f"successful"
            )

            all_results.extend(results)

    return all_results


# output
RAW_FIELDS = [
    "tool",
    "target",
    "url",
    "api_status_code",
    "target_status_code",
    "response_ms",
    "has_title",
    "has_expected_content",
    "title",
    "content_type",
    "success",
    "error",
]


def write_raw(
    results: list[dict],
    tool: str,
    timestamp: str,
):

    path = (
        Path("results")
        / f"raw_{tool}_{timestamp}.csv"
    )

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=RAW_FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(results)

    print(
        f"\nRaw results -> {path}"
    )


def percentile(
    sorted_values: list[int],
    percentile_value: float,
) -> int:

    if not sorted_values:
        return 0

    index = max(
        0,
        min(
            len(sorted_values) - 1,
            int(
                len(sorted_values)
                * percentile_value
            ) - 1,
        ),
    )

    return sorted_values[index]


def write_summary(
    results: list[dict],
    tool: str,
    timestamp: str,
):

    import statistics

    by_target: dict[str, list] = {}

    for result in results:

        by_target.setdefault(
            result["target"],
            [],
        ).append(result)

    path = (
        Path("results")
        / f"summary_{tool}_{timestamp}.csv"
    )

    fields = [
        "tool",
        "target",
        "url",
        "total",
        "successful",
        "failed",
        "success_rate_pct",
        "avg_ms",
        "p50_ms",
        "p95_ms",
    ]

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for target, requests in by_target.items():

            times = sorted(
                result["response_ms"]
                for result in requests
            )

            total = len(requests)

            successful = sum(
                1
                for result in requests
                if result["success"]
            )

            writer.writerow(
                {
                    "tool": tool,
                    "target": target,
                    "url": requests[0]["url"],
                    "total": total,
                    "successful": successful,
                    "failed": (
                        total - successful
                    ),
                    "success_rate_pct": round(
                        successful
                        / total
                        * 100,
                        1,
                    ),
                    "avg_ms": round(
                        statistics.mean(times)
                    ),
                    "p50_ms": percentile(
                        times,
                        0.50,
                    ),
                    "p95_ms": percentile(
                        times,
                        0.95,
                    ),
                }
            )

    print(
        f"Summary -> {path}"
    )


def print_table(
    results: list[dict],
    tool: str,
):

    import statistics

    by_target: dict[str, list] = {}

    for result in results:

        by_target.setdefault(
            result["target"],
            [],
        ).append(result)

    print("\n" + "=" * 85)
    print(f"  {'ZENROWS' if tool == 'zenrows' else tool.upper()}")
    print("=" * 85)

    print(
        f"  {'Target':<38} "
        f"{'OK':>5} "
        f"{'Total':>6} "
        f"{'Rate':>8} "
        f"{'Avg ms':>9}"
    )

    print("-" * 85)

    for target, requests in by_target.items():

        successful = sum(
            1
            for result in requests
            if result["success"]
        )

        avg = round(
            statistics.mean(
                result["response_ms"]
                for result in requests
            )
        )

        print(
            f"  {target[:38]:<38} "
            f"{successful:>5} "
            f"{len(requests):>6} "
            f"{successful / len(requests) * 100:>7.1f}% "
            f"{avg:>8}ms"
        )

    print("=" * 85)


# entrypoint
def main():

    global REQUESTS_PER_TARGET

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--tool",
        choices=[
            "zenrows",
            "browserbase",
            "both",
        ],
        default="both",
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=REQUESTS_PER_TARGET,
    )

    args = parser.parse_args()

    REQUESTS_PER_TARGET = args.requests

    if (
        args.tool in (
            "zenrows",
            "both",
        )
        and not ZENROWS_API_KEY
    ):

        print(
            "ERROR: ZENROWS_API_KEY "
            "not set in .env"
        )

        return

    if (
        args.tool in (
            "browserbase",
            "both",
        )
        and not BROWSERBASE_API_KEY
    ):

        print(
            "ERROR: BROWSERBASE_API_KEY "
            "not set in .env"
        )

        return

    ensure_results_dir()

    timestamp = now_ts()

    tools = (
        ["zenrows", "browserbase"]
        if args.tool == "both"
        else [args.tool]
    )

    for tool in tools:

        print("\n" + "=" * 85)

        print(
            f"  {tool.upper()} - "
            f"{len(TARGETS)} targets x "
            f"{REQUESTS_PER_TARGET} requests @ "
            f"{RATE_PER_SECOND} req/s"
        )

        print("=" * 85)

        results = asyncio.run(
            run_tool(
                tool,
                TARGETS,
            )
        )

        print_table(
            results,
            tool,
        )

        write_raw(
            results,
            tool,
            timestamp,
        )

        write_summary(
            results,
            tool,
            timestamp,
        )


if __name__ == "__main__":
    main()