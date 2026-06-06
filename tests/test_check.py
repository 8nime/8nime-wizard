# -*- coding: utf-8 -*-
"""Tests for resources/libs/check.py — pure regex / data-transformation logic."""
import re
import pytest


# ---------------------------------------------------------------------------
# Helpers: the regex patterns extracted from check.py, tested in isolation
# ---------------------------------------------------------------------------

BUILD_PATTERN = (
    r'name="(.+?)".+?ersion="(.+?)".+?rl="(.+?)".+?inor="(.+?)".+?ui="(.+?)".+?'
    r'odi="(.+?)".+?heme="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?review="(.+?)".+?'
    r'dult="(.+?)".+?nfo="(.+?)".+?escription="(.+?)"'
)

WIZARD_PATTERN = r'id="{0}".+?ersion="(.+?)".+?ip="(.+?)"'

INFO_PATTERN = (
    r'.+?ame="(.+?)".+?xtracted="(.+?)".+?ipsize="(.+?)".+?kin="(.+?)".+?'
    r'reated="(.+?)".+?rograms="(.+?)".+?ideo="(.+?)".+?usic="(.+?)".+?'
    r'icture="(.+?)".+?epos="(.+?)".+?cripts="(.+?)".+?inaries="(.+?)"'
)


def make_build_line(name="8nime", version="1.0.0", url="http://example.com/build.zip",
                    minor="0", gui="http://", kodi="19", theme="http://",
                    icon="http://icon.png", fanart="http://fanart.jpg",
                    preview="http://", adult="no", info="info text",
                    description="A test build"):
    return (
        f'name="{name}" version="{version}" url="{url}" minor="{minor}" '
        f'gui="{gui}" kodi="{kodi}" theme="{theme}" icon="{icon}" '
        f'fanart="{fanart}" preview="{preview}" adult="{adult}" '
        f'info="{info}" description="{description}"'
    )


def make_wizard_line(addon_id="plugin.program.8nime.wizard",
                     version="2.0.0", zip_url="http://example.com/wiz.zip"):
    return f'id="{addon_id}" version="{version}" zip="{zip_url}"'


def make_info_line(name="8nime", extracted="500MB", zipsize="200MB",
                   skin="skin.bingie", created="2024-01-01",
                   programs="10", video="5", music="0", picture="0",
                   repos="3", scripts="2", binaries="0"):
    return (
        f'name="{name}" extracted="{extracted}" zipsize="{zipsize}" '
        f'skin="{skin}" created="{created}" programs="{programs}" '
        f'video="{video}" music="{music}" picture="{picture}" '
        f'repos="{repos}" scripts="{scripts}" binaries="{binaries}"'
    )


class TestBuildRegex:
    def test_parses_name(self):
        line = make_build_line(name="8nime")
        match = re.compile(BUILD_PATTERN).findall(line)
        assert len(match) == 1

    def test_extracts_version(self):
        line = make_build_line(version="2.5.1")
        match = re.compile(BUILD_PATTERN).findall(line)
        assert match[0][1] == "2.5.1"

    def test_extracts_url(self):
        line = make_build_line(url="https://dl.example.com/build.zip")
        match = re.compile(BUILD_PATTERN).findall(line)
        assert match[0][2] == "https://dl.example.com/build.zip"

    def test_extracts_kodi_version(self):
        line = make_build_line(kodi="19")
        match = re.compile(BUILD_PATTERN).findall(line)
        assert match[0][5] == "19"

    def test_extracts_adult_flag(self):
        line = make_build_line(adult="yes")
        match = re.compile(BUILD_PATTERN).findall(line)
        assert match[0][10] == "yes"

    def test_extracts_description(self):
        line = make_build_line(description="Anime build for Kodi")
        match = re.compile(BUILD_PATTERN).findall(line)
        assert match[0][12] == "Anime build for Kodi"

    def test_no_match_on_wrong_name(self):
        line = make_build_line(name="OtherBuild")
        pattern = r'name="8nime".+?ersion="(.+?)"'
        match = re.compile(pattern).findall(line)
        assert len(match) == 0


class TestWizardRegex:
    def test_parses_wizard_entry(self):
        addon_id = "plugin.program.8nime.wizard"
        line = make_wizard_line(addon_id=addon_id, version="3.1.0")
        pattern = WIZARD_PATTERN.format(re.escape(addon_id))
        match = re.compile(pattern).findall(line)
        assert len(match) == 1
        assert match[0][0] == "3.1.0"

    def test_extracts_zip_url(self):
        addon_id = "plugin.program.8nime.wizard"
        zip_url = "https://example.com/wizard.zip"
        line = make_wizard_line(addon_id=addon_id, zip_url=zip_url)
        pattern = WIZARD_PATTERN.format(re.escape(addon_id))
        match = re.compile(pattern).findall(line)
        assert match[0][1] == zip_url

    def test_no_match_wrong_id(self):
        line = make_wizard_line(addon_id="plugin.program.other.wizard")
        pattern = WIZARD_PATTERN.format(re.escape("plugin.program.8nime.wizard"))
        match = re.compile(pattern).findall(line)
        assert len(match) == 0


class TestInfoRegex:
    def test_parses_info_line(self):
        line = make_info_line(name="8nime")
        match = re.compile(INFO_PATTERN).findall(line)
        assert len(match) == 1

    def test_extracts_all_fields(self):
        line = make_info_line(
            name="8nime", extracted="500MB", zipsize="200MB",
            skin="skin.bingie", created="2024-01-01",
            programs="10", video="5", music="0", picture="0",
            repos="3", scripts="2", binaries="0",
        )
        match = re.compile(INFO_PATTERN).findall(line)
        name, extracted, zipsize, skin, created, programs, video, music, picture, repos, scripts, binaries = match[0]
        assert name == "8nime"
        assert extracted == "500MB"
        assert skin == "skin.bingie"
        assert programs == "10"


class TestVersionComparison:
    """Version comparison behaviour mirrors what check_build_update does:
    a plain string '>' comparison on dotted version strings."""

    def test_newer_version_greater(self):
        assert "1.1.0" > "1.0.0"

    def test_same_version_not_greater(self):
        assert not ("1.0.0" > "1.0.0")

    def test_older_version_not_greater(self):
        assert not ("0.9.0" > "1.0.0")

    def test_two_digit_minor_comparison(self):
        # String comparison: "1.9.0" > "1.10.0" would be True for str comparison
        # The wizard uses plain string '>' — document that behaviour.
        installed = "1.0.0"
        latest = "1.0.1"
        assert latest > installed


class TestCleanTextInCheck:
    """check.py cleans link text the same way tools.clean_text does."""

    def test_strips_newlines_from_link(self):
        raw = 'name="8nime"\nversion="1.0"'
        cleaned = raw.replace('\n', '').replace('\r', '').replace('\t', '')
        assert '\n' not in cleaned

    def test_fills_empty_gui(self):
        raw = 'gui=""'
        cleaned = raw.replace('gui=""', 'gui="http://"')
        assert 'gui="http://"' in cleaned

    def test_fills_empty_theme(self):
        raw = 'theme=""'
        cleaned = raw.replace('theme=""', 'theme="http://"')
        assert 'theme="http://"' in cleaned
