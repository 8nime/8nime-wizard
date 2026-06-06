# -*- coding: utf-8 -*-
"""Tests for resources/libs/downloader.py — URL construction and file write logic."""
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch, mock_open


class TestDownloaderInit:
    def test_instantiates(self):
        from resources.libs.downloader import Downloader
        d = Downloader()
        assert d is not None
        assert hasattr(d, "download")


class TestDownloaderDownload:
    """Test Downloader.download with a fully mocked HTTP response."""

    def _make_mock_response(self, content=b"fake zip data", content_length=None):
        response = MagicMock()
        response.headers = {}
        if content_length is not None:
            response.headers["content-length"] = str(content_length)
        response.content = content
        response.iter_content = MagicMock(return_value=[content])
        return response

    def test_download_creates_file(self):
        from resources.libs.downloader import Downloader

        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "build.zip")
            fake_content = b"PK\x03\x04fake zip"

            with patch("resources.libs.common.tools.open_url") as mock_open_url, \
                 patch("resources.libs.common.tools._check_url", return_value=True):
                mock_resp = self._make_mock_response(content=fake_content)
                mock_open_url.return_value = mock_resp

                d = Downloader()
                d.download("https://example.com/build.zip", dest)

            assert os.path.exists(dest)
            with open(dest, "rb") as f:
                written = f.read()
            assert written == fake_content

    def test_download_creates_parent_directory(self):
        from resources.libs.downloader import Downloader

        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "subdir", "build.zip")

            with patch("resources.libs.common.tools.open_url") as mock_open_url, \
                 patch("resources.libs.common.tools._check_url", return_value=True):
                mock_resp = self._make_mock_response(content=b"data")
                mock_open_url.return_value = mock_resp

                d = Downloader()
                d.download("https://example.com/build.zip", dest)

            assert os.path.isdir(os.path.join(tmpdir, "subdir"))

    def test_download_no_op_when_url_invalid(self):
        from resources.libs.downloader import Downloader

        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "build.zip")

            with patch("resources.libs.common.tools.open_url", return_value=False):
                d = Downloader()
                d.download("https://example.com/build.zip", dest)

            # The Downloader opens the file before calling open_url, so the file
            # exists but is empty when the URL is invalid.
            assert os.path.exists(dest)
            assert os.path.getsize(dest) == 0

    def test_download_with_content_length_writes_chunks(self):
        from resources.libs.downloader import Downloader

        chunk = b"A" * 1024
        total = len(chunk)

        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "build.zip")

            with patch("resources.libs.common.tools.open_url") as mock_open_url, \
                 patch("resources.libs.common.tools._check_url", return_value=True):
                mock_resp = self._make_mock_response(content=chunk, content_length=total)
                mock_open_url.return_value = mock_resp

                d = Downloader()
                d.download("https://example.com/build.zip", dest)

            assert os.path.exists(dest)


class TestUrlConstruction:
    """Test that URL helpers produce valid URLs for known patterns."""

    def test_buildfile_url_is_valid(self):
        import uservar
        from resources.libs.common.tools import _is_url
        assert _is_url(uservar.BUILDFILE)

    def test_addonfile_url_is_valid(self):
        import uservar
        from resources.libs.common.tools import _is_url
        assert _is_url(uservar.ADDONFILE)

    def test_repoaddonxml_url_is_valid(self):
        import uservar
        from resources.libs.common.tools import _is_url
        assert _is_url(uservar.REPOADDONXML)

    def test_repozipurl_is_valid(self):
        import uservar
        from resources.libs.common.tools import _is_url
        assert _is_url(uservar.REPOZIPURL)

    def test_notification_url_is_valid(self):
        import uservar
        from resources.libs.common.tools import _is_url
        assert _is_url(uservar.NOTIFICATION)
