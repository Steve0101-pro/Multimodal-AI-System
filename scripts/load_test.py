"""Small authenticated health-check load test for staging only."""

import argparse
import asyncio
import time

import httpx


async def run(base_url: str, requests: int, concurrency: int) -> None:
    semaphore = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(base_url=base_url, timeout=10) as client:
        async def call() -> float:
            async with semaphore:
                started = time.perf_counter()
                response = await client.get("/")
                response.raise_for_status()
                return time.perf_counter() - started

        durations = await asyncio.gather(*(call() for _ in range(requests)))
    durations.sort()
    print({"requests": requests, "concurrency": concurrency, "p50_ms": round(durations[len(durations) // 2] * 1000, 2), "p95_ms": round(durations[max(0, int(len(durations) * .95) - 1)] * 1000, 2)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(run(args.url, args.requests, args.concurrency))