from __future__ import annotations

import io
import sys
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from zspeedtest.main import SpeedTestArgs, _format_size, download_url, run

_4K = 4096
_1M = 1024 * 1024


def _create_mock_response(data: bytes) -> io.BytesIO:
    mock_io_bytes = MagicMock(wraps=io.BytesIO, spec=io.BytesIO)
    mock_response = mock_io_bytes(data)
    mock_response.__enter__ = lambda _: mock_response
    mock_response.__exit__ = lambda *_: None
    return cast("io.BytesIO", mock_response)


class TestFormatSize:
    def test_bytes(self) -> None:
        assert _format_size(0) == "0.0 B"
        assert _format_size(512) == "512.0 B"
        assert _format_size(1023) == "1023.0 B"

    def test_kilobytes(self) -> None:
        assert _format_size(1024) == "1.0 KB"
        assert _format_size(2048) == "2.0 KB"
        assert _format_size(1536) == "1.5 KB"

    def test_megabytes(self) -> None:
        assert _format_size(1024**2) == "1.0 MB"
        assert _format_size(5 * 1024**2) == "5.0 MB"

    def test_gigabytes(self) -> None:
        assert _format_size(1024**3) == "1.0 GB"
        assert _format_size(3 * 1024**3) == "3.0 GB"

    def test_terabytes(self) -> None:
        assert _format_size(1024**4) == "1.0 TB"
        assert _format_size(2.5 * 1024**4) == "2.5 TB"


class TestDownloadUrl:
    def test_successful_download(self) -> None:
        mock_response = _create_mock_response(b"x" * _4K)
        mock_progress_bar = MagicMock()

        req = MagicMock()
        with patch("zspeedtest.main.urlopen", return_value=mock_response):
            result = download_url(req, timeout=10, progress_bar=mock_progress_bar)

        assert result.bytes_downloaded == _4K
        assert result.duration_seconds > 0
        mock_progress_bar.on_progress.assert_called()
        mock_progress_bar.finish.assert_called_once()

    def test_empty_response(self) -> None:
        mock_response = _create_mock_response(b"")
        mock_progress_bar = MagicMock()

        req = MagicMock()
        with patch("zspeedtest.main.urlopen", return_value=mock_response):
            result = download_url(req, timeout=10, progress_bar=mock_progress_bar)

        assert result.bytes_downloaded == 0
        assert result.duration_seconds == 0
        mock_progress_bar.on_progress.assert_not_called()
        mock_progress_bar.finish.assert_called_once()

    def test_large_download(self) -> None:
        mock_response = _create_mock_response(b"y" * (1024 * 128))
        mock_progress_bar = MagicMock()

        req = MagicMock()
        with patch("zspeedtest.main.urlopen", return_value=mock_response):
            result = download_url(req, timeout=10, progress_bar=mock_progress_bar)

        assert result.bytes_downloaded == 1024 * 128
        mock_progress_bar.on_progress.assert_called()
        mock_progress_bar.finish.assert_called_once()


class TestSpeedTestArgs:
    def test_default_url(self) -> None:
        test_argv = ["prog"]
        with patch.object(sys, "argv", test_argv):
            args = SpeedTestArgs.from_cli()

        assert args.url == "http://ipv4.download.thinkbroadband.com/10MB.zip"
        assert args.requests == 10
        assert args.timeout == 30

    def test_custom_url(self) -> None:
        test_argv = ["prog", "http://example.com/file.bin"]

        with patch.object(sys, "argv", test_argv):
            args = SpeedTestArgs.from_cli()

        assert args.url == "http://example.com/file.bin"

    def test_custom_requests(self) -> None:
        test_argv = ["prog", "http://example.com/file.bin", "--requests", "5"]

        with patch.object(sys, "argv", test_argv):
            args = SpeedTestArgs.from_cli()

        assert args.requests == 5

    def test_custom_timeout(self) -> None:
        test_argv = ["prog", "http://example.com/file.bin", "--timeout", "60"]

        with patch.object(sys, "argv", test_argv):
            args = SpeedTestArgs.from_cli()

        assert args.timeout == 60

    def test_short_flags(self) -> None:
        test_argv = [
            "prog",
            "http://example.com/file.bin",
            "-n",
            "3",
            "-t",
            "15",
        ]

        with patch.object(sys, "argv", test_argv):
            args = SpeedTestArgs.from_cli()

        assert args.requests == 3
        assert args.timeout == 15

    def test_invalid_url_raises(self) -> None:
        test_argv = ["prog", "ftp://example.com/file.bin"]
        with (
            patch.object(sys, "argv", test_argv),
            pytest.raises(ValueError, match="URL must start with"),
        ):
            SpeedTestArgs.from_cli()


class TestRun:
    def test_successful_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        data = b"a" * _1M

        def make_response(*_: object, **__: object) -> io.BytesIO:
            return _create_mock_response(data)

        test_argv = ["prog", "http://example.com/file.bin", "--requests", "2"]

        with (
            patch.object(sys, "argv", test_argv),
            patch("zspeedtest.main.urlopen", side_effect=make_response),
        ):
            run()

        captured = capsys.readouterr()
        assert "Successful requests : 2 / 2" in captured.out
        assert "MB/s" in captured.out
        assert "ERROR" not in captured.out

    def test_all_requests_fail(self, capsys: pytest.CaptureFixture[str]) -> None:
        test_argv = ["prog", "http://example.com/file.bin", "--requests", "3"]

        with (
            patch.object(sys, "argv", test_argv),
            patch(
                "zspeedtest.main.urlopen",
                side_effect=ConnectionError("connection failed"),
            ),
            pytest.raises(SystemExit) as exc,
        ):
            run()

        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "No requests completed successfully" in captured.out

    def test_partial_failures(self, capsys: pytest.CaptureFixture[str]) -> None:
        data = b"b" * 4096

        def make_response(*_: object, **__: object) -> io.BytesIO:
            return _create_mock_response(data)

        call_count: int = 0

        def side_effect(*_: object, **__: object) -> io.BytesIO:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                msg = "timeout"
                raise TimeoutError(msg)
            return make_response()

        test_argv = ["prog", "http://example.com/file.bin", "--requests", "3"]

        with (
            patch.object(sys, "argv", test_argv),
            patch("zspeedtest.main.urlopen", side_effect=side_effect),
        ):
            run()

        captured = capsys.readouterr()
        assert "Successful requests : 2 / 3" in captured.out
        assert "ERROR: timeout" in captured.out
        assert "MB/s" in captured.out
