# -*- coding: utf-8 -*-
"""Tests for resources/libs/common/tools.py — pure utility functions."""
import os
import tempfile
import pytest


class TestConvertSize:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_bytes(self):
        assert self.tools.convert_size(512) == "512.00 B"

    def test_kilobytes(self):
        result = self.tools.convert_size(1024)
        assert "K" in result

    def test_megabytes(self):
        result = self.tools.convert_size(1024 * 1024)
        assert "M" in result

    def test_gigabytes(self):
        result = self.tools.convert_size(1024 * 1024 * 1024)
        assert "G" in result


class TestPercentage:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_half(self):
        assert self.tools.percentage(50, 100) == 50.0

    def test_full(self):
        assert self.tools.percentage(100, 100) == 100.0

    def test_zero(self):
        assert self.tools.percentage(0, 100) == 0.0

    def test_fractional(self):
        result = self.tools.percentage(1, 3)
        assert abs(result - 33.333) < 0.01


class TestIsUrl:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_valid_http_url(self):
        assert self.tools._is_url("http://example.com") is True

    def test_valid_https_url(self):
        assert self.tools._is_url("https://example.com/path") is True

    def test_not_a_url(self):
        assert self.tools._is_url("not-a-url") is False

    def test_empty_string(self):
        assert self.tools._is_url("") is False

    def test_path_only(self):
        assert self.tools._is_url("/tmp/somefile.zip") is False


class TestIdGenerator:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_default_length(self):
        result = self.tools.id_generator()
        assert len(result) == 6

    def test_custom_length(self):
        result = self.tools.id_generator(size=10)
        assert len(result) == 10

    def test_uppercase_digits(self):
        import string
        result = self.tools.id_generator(size=20)
        valid = set(string.ascii_uppercase + string.digits)
        assert all(c in valid for c in result)

    def test_randomness(self):
        results = {self.tools.id_generator() for _ in range(20)}
        assert len(results) > 1


class TestGetDate:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_returns_float_unformatted(self):
        result = self.tools.get_date()
        assert isinstance(result, float)

    def test_formatted_returns_string(self):
        result = self.tools.get_date(formatted=True)
        assert isinstance(result, str)
        assert "-" in result

    def test_future_date_greater(self):
        now = self.tools.get_date(days=0)
        future = self.tools.get_date(days=1)
        assert future > now

    def test_past_date_lesser(self):
        now = self.tools.get_date(days=0)
        past = self.tools.get_date(days=-1)
        assert past < now


class TestReadWriteFile:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_write_and_read(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            tmp = f.name
        try:
            self.tools.write_to_file(tmp, "hello world")
            content = self.tools.read_from_file(tmp)
            assert content == "hello world"
        finally:
            os.unlink(tmp)

    def test_write_appends_with_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            tmp = f.name
        try:
            self.tools.write_to_file(tmp, "first")
            self.tools.write_to_file(tmp, "second", mode='a')
            content = self.tools.read_from_file(tmp)
            assert content == "firstsecond"
        finally:
            os.unlink(tmp)


class TestCleanText:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_strips_newlines(self):
        assert "\n" not in self.tools.clean_text("a\nb")

    def test_strips_tabs(self):
        assert "\t" not in self.tools.clean_text("a\tb")

    def test_strips_carriage_return(self):
        assert "\r" not in self.tools.clean_text("a\rb")

    def test_replaces_empty_gui(self):
        result = self.tools.clean_text('gui=""')
        assert 'gui="http://"' in result

    def test_replaces_empty_theme(self):
        result = self.tools.clean_text('theme=""')
        assert 'theme="http://"' in result

    def test_replaces_empty_adult(self):
        result = self.tools.clean_text('adult=""')
        assert 'adult="no"' in result


class TestChunks:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_even_split(self):
        result = list(self.tools.chunks("abcdef", 2))
        assert result == ["ab", "cd", "ef"]

    def test_uneven_split(self):
        result = list(self.tools.chunks("abcde", 2))
        assert result == ["ab", "cd", "e"]

    def test_chunk_larger_than_string(self):
        result = list(self.tools.chunks("abc", 10))
        assert result == ["abc"]


class TestFileCount:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_counts_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ("a.txt", "b.txt", "c.txt"):
                open(os.path.join(tmpdir, name), "w").close()
            count = self.tools.file_count(tmpdir, excludes=False)
            assert count == 3

    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            count = self.tools.file_count(tmpdir, excludes=False)
            assert count == 0


class TestDataType:
    def setup_method(self):
        from resources.libs.common import tools
        self.tools = tools

    def test_string(self):
        assert self.tools.data_type("hello") == "str"

    def test_int(self):
        assert self.tools.data_type(42) == "int"

    def test_list(self):
        assert self.tools.data_type([]) == "list"
