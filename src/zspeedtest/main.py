"""Internet speed tester.

Usage: zspeedtest <URL> [--requests N]
"""

import argparse
import sys
import time
from collections.abc import Callable
from functools import partial
from typing import NamedTuple
from urllib.request import Request, urlopen

KB = 1024
MB = KB**2
CHUNK_SIZE = KB * 64


def _write_stdout(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


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
            default="http://ipv4.download.thinkbroadband.com/10MB.zip",
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


def download_url(
    req: Request,
    timeout: int,
    on_progress: Callable[[float, float], None] = lambda _, __: None,
) -> RequestResult:
    total_bytes: int = 0
    total_time: float = 0
    on_progress(total_bytes, total_time)

    start = time.perf_counter()
    # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected  # noqa: E501, ERA001
    with urlopen(req, timeout=timeout) as response:  # nosec
        while chunk := response.read(CHUNK_SIZE):
            total_bytes += len(chunk)
            total_time = time.perf_counter() - start
            on_progress(total_bytes, total_time)

    return RequestResult(
        duration_seconds=total_time,
        bytes_downloaded=total_bytes,
    )


def format_size(bytes_count: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_count < KB:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= KB
    return f"{bytes_count:.1f} TB"


def write_progress_bar(number: int, current_bytes: float, current_time: float) -> None:
    speed_mbps = (current_bytes / current_time) / MB if current_time > 0 else 0.0
    _write_stdout(
        f"\r{number:>3}  {format_size(current_bytes):>10}"
        f"  {current_time:>7.2f}s  {speed_mbps:>10.2f} MB/s"
    )


def run() -> None:
    args = SpeedTestArgs.from_cli()
    _write_stdout(
        f"URL: {args.url}\n"
        f"Requests: {args.requests}\n"
        f"{'-' * 52}\n"
        f"{'#':>3}  {'Size':>10}  {'Time':>8}  {'Speed':>12}\n"
        f"{'-' * 52}\n"
    )

    results: list[RequestResult] = []

    req = Request(args.url)
    req.add_header("User-Agent", "zspeedtest/1.0")

    for i in range(1, args.requests + 1):
        try:
            r = download_url(
                req,
                timeout=args.timeout,
                on_progress=partial(write_progress_bar, i),
            )
            _write_stdout("\n")
        except Exception as e:  # noqa: BLE001
            _write_stdout(f"{i:>3}  ERROR: {e}")
            continue

        results.append(r)

    if not results:
        _write_stdout("\nNo requests completed successfully.")
        sys.exit(1)
    _write_stdout("=" * 52 + "\n")

    total_bytes = sum(r.bytes_downloaded for r in results)
    total_time = sum(r.duration_seconds for r in results)
    avg_time = total_time / len(results)
    avg_speed = (total_bytes / total_time) / MB
    min_speed = min((r.bytes_downloaded / r.duration_seconds) / MB for r in results)
    max_speed = max((r.bytes_downloaded / r.duration_seconds) / MB for r in results)
    _write_stdout(
        f"Successful requests : {len(results)} / {args.requests}\n"
        f"Total downloaded    : {format_size(total_bytes)}\n"
        f"Average time        : {avg_time:.2f} s\n"
        f"Average speed       : {avg_speed:.2f} MB/s\n"
        f"Min / Max           : {min_speed:.2f} / {max_speed:.2f} MB/s\n"
    )
