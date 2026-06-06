# -*- coding: utf-8 -*-
"""Tests for uservar.py — build configuration constants."""
import pytest
import uservar


class TestAddonIdentity:
    def test_addontitle_contains_8nime(self):
        assert "8nime" in uservar.ADDONTITLE

    def test_buildername(self):
        assert uservar.BUILDERNAME == "8nime"

    def test_repoid_is_8nime_repo(self):
        assert uservar.REPOID == "repository.8nime"

    def test_excludes_contains_repoid(self):
        assert "repository.8nime" in uservar.EXCLUDES

    def test_autoupdate_yes(self):
        assert uservar.AUTOUPDATE == "Yes"

    def test_autoinstall_yes(self):
        assert uservar.AUTOINSTALL == "Yes"


class TestBaseUrl:
    def test_base_url_references_8nime_repo(self):
        assert "8nime" in uservar.BASE_URL

    def test_buildfile_uses_base_url(self):
        assert uservar.BUILDFILE.startswith(uservar.BASE_URL)

    def test_youtubefile_uses_base_url(self):
        assert uservar.YOUTUBEFILE.startswith(uservar.BASE_URL)

    def test_addonfile_uses_base_url(self):
        assert uservar.ADDONFILE.startswith(uservar.BASE_URL)

    def test_advancedfile_uses_base_url(self):
        assert uservar.ADVANCEDFILE.startswith(uservar.BASE_URL)

    def test_repoaddonxml_uses_base_url(self):
        assert uservar.REPOADDONXML.startswith(uservar.BASE_URL)

    def test_repozipurl_uses_base_url(self):
        assert uservar.REPOZIPURL.startswith(uservar.BASE_URL)

    def test_notification_uses_base_url(self):
        assert uservar.NOTIFICATION.startswith(uservar.BASE_URL)


class TestTheme:
    def test_color1_is_deeppink(self):
        assert uservar.COLOR1 == "deeppink"

    def test_color2_is_white(self):
        assert uservar.COLOR2 == "white"

    def test_theme1_formats_with_name(self):
        result = uservar.THEME1.format("Builds")
        assert "8nime" in result
        assert "Builds" in result

    def test_theme4_contains_current_build_label(self):
        result = uservar.THEME4.format("MyBuild")
        assert "Current Build" in result
        assert "MyBuild" in result

    def test_theme5_contains_current_theme_label(self):
        result = uservar.THEME5.format("MyTheme")
        assert "Current Theme" in result
        assert "MyTheme" in result


class TestNotification:
    def test_notification_enabled(self):
        assert uservar.ENABLE == "Yes"

    def test_header_message_contains_8nime(self):
        assert "8nime" in uservar.HEADERMESSAGE

    def test_headertype_is_text(self):
        assert uservar.HEADERTYPE == "Text"


class TestUpdatecheck:
    def test_updatecheck_is_integer(self):
        assert isinstance(uservar.UPDATECHECK, int)
