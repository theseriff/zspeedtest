# zspeedtest

Simple CLI internet speed tester. Downloads a file and measures throughput.

```bash
pip install zspeedtest
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
