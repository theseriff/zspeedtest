<div align="center">

<h1>zspeedtest</h1>
<p><strong>Simple CLI internet speed tester. Downloads a file and measures throughput.</strong></p>

[![Supported Python versions](https://img.shields.io/pypi/pyversions/zspeedtest.svg)](https://pypi.org/project/zspeedtest)
[![PyPI version](https://badge.fury.io/py/zspeedtest.svg)](https://pypi.python.org/pypi/zspeedtest)
[![Tests](https://github.com/theseriff/zspeedtest/actions/workflows/pr_tests.yml/badge.svg)](https://github.com/theseriff/zspeedtest/actions/workflows/pr_tests.yml)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/theseriff/zspeedtest.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/theseriff/zspeedtest)
[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/theseriff/zspeedtest?utm_source=badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

```bash
uv add zspeedtest
zspeedtest
```

## Usage

```
zspeedtest [URL] [--requests N] [--timeout N]
```

- `URL` — large file to download (default: 10MB test file from ThinkBroadband)
- `--requests`/`-n` — number of test requests (default: 10)
- `--timeout`/`-t` — per-request timeout in seconds (default: 30)

### Examples

```bash
zspeedtest
zspeedtest http://example.com/file.bin --requests 5
zspeedtest http://example.com/file.bin -n 3 -t 15
```
