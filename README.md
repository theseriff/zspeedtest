<div align="center">

<h1>zspeedtest</h1>
<p><strong>Simple CLI internet speed tester. Downloads a file and measures throughput.</strong></p>

[![Supported Python versions](https://img.shields.io/pypi/pyversions/zspeedtest.svg)](https://pypi.org/project/zspeedtest)
[![PyPI version](https://badge.fury.io/py/zspeedtest.svg)](https://pypi.python.org/pypi/zspeedtest)
[![Tests](https://github.com/theseriff/zspeedtest/actions/workflows/pr_tests.yaml/badge.svg)](https://github.com/theseriff/zspeedtest/actions/workflows/pr_tests.yaml)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/theseriff/zspeedtest.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/theseriff/zspeedtest)
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

Output:

```bash
URL: http://ipv4.download.thinkbroadband.com/10MB.zip
Requests: 1
----------------------------------------------------
  #        Size      Time         Speed
----------------------------------------------------

  1     10.0 MB    29.95s        0.33 MB/s
====================================================
Successful requests : 1 / 1
Total downloaded    : 10.0 MB
Average time        : 29.95 s
Average speed       : 0.33 MB/s
Min / Max           : 0.33 / 0.33 MB/s
```
