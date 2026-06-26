"""Internet speed tester.

Usage: zspeedtest <URL> [--requests N]
"""

import argparse
import sys
import textwrap
import time
from typing import NamedTuple
from urllib.request import Request, urlopen

KB = 1024
MB = KB**2
CHUNK_SIZE = KB * 64
DEFAULT_URL = "http://ipv4.download.thinkbroadband.com/10MB.zip"


class SpeedTestArgs(NamedTuple):
    url: str
    requests: int
    timeout: int

    @classmethod
    def from_cli(cls) -> "SpeedTestArgs":
        parser = argparse.ArgumentParser(
            description="Internet speed tester",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "url",
            nargs="?",
            default=DEFAULT_URL,
            help="URL of a large file to download",
        )
        parser.add_argument(
            "--requests",
            "-n",
            type=int,
            default=10,
            metavar="N",
            help="Number of requests",
        )
        parser.add_argument(
            "--timeout",
            "-t",
            type=int,
            default=30,
            metavar="N",
            help="Request timeout",
        )
        namespace = parser.parse_args()

        if not namespace.url.startswith(("http:", "https:")):
            msg = "URL must start with 'http:' or 'https:'"
            raise ValueError(msg)

        return cls(**namespace.__dict__)


class RequestResult(NamedTuple):
    duration_seconds: float
    bytes_downloaded: int


def download_url(req: Request, timeout: int) -> RequestResult:
    start = time.perf_counter()
    total_bytes: int = 0

    # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected  # noqa: E501, ERA001
    with urlopen(req, timeout=timeout) as response:  # nosec
        while chunk := response.read(CHUNK_SIZE):
            total_bytes += len(chunk)

    duration = time.perf_counter() - start
    return RequestResult(
        duration_seconds=duration,
        bytes_downloaded=total_bytes,
    )


def format_size(bytes_count: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_count < KB:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= KB
    return f"{bytes_count:.1f} TB"


def run() -> None:
    args = SpeedTestArgs.from_cli()
    start_info = textwrap.dedent(f"""
        URL: {args.url}
        Requests: {args.requests}
        {"-" * 52}
        {"#":>3}  {"Size":>10}  {"Time":>8}  {"Speed":>12}
        {"-" * 52}
    """)
    print(start_info)

    results: list[RequestResult] = []

    req = Request(args.url)
    req.add_header("User-Agent", "zspeedtest/1.0")

    for i in range(args.requests):
        try:
            r = download_url(req, timeout=args.timeout)
        except Exception as e:  # noqa: BLE001
            print(f"{i + 1:>3}  ERROR: {e}")
            continue

        results.append(r)

        speed_mbps = (r.bytes_downloaded / r.duration_seconds) / MB
        print(
            f"{i:>3}  {format_size(r.bytes_downloaded):>10}"
            f"  {r.duration_seconds:>7.2f}s  {speed_mbps:>10.2f} MB/s"
        )

    if not results:
        print("\nNo requests completed successfully.")
        sys.exit(1)

    print("=" * 52)

    total_bytes = sum(r.bytes_downloaded for r in results)
    total_time = sum(r.duration_seconds for r in results)
    avg_time = total_time / len(results)
    avg_speed = (total_bytes / total_time) / MB
    min_speed = min(
        (r.bytes_downloaded / r.duration_seconds) / MB for r in results
    )
    max_speed = max(
        (r.bytes_downloaded / r.duration_seconds) / MB for r in results
    )

    end_info = textwrap.dedent(f"""
        Successful requests : {len(results)} / {args.requests}
        Total downloaded    : {format_size(total_bytes)}
        Average time        : {avg_time:.2f} s
        Average speed       : {avg_speed:.2f} MB/s
        Min / Max           : {min_speed:.2f} / {max_speed:.2f} MB/s
    """)
    print(end_info)


if __name__ == "__main__":
    run()
