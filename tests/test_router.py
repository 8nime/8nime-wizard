# -*- coding: utf-8 -*-
"""Tests for resources/libs/common/router.py — parameter parsing and dispatch routing."""
import sys
import pytest
from unittest.mock import MagicMock, patch


class TestRouterParamParsing:
    def setup_method(self):
        from resources.libs.common.router import Router
        self.Router = Router

    def _make_router(self):
        with patch("resources.libs.common.tools.ensure_folders"):
            return self.Router()

    def test_empty_paramstring_yields_empty_params(self):
        router = self._make_router()
        params = router._log_params("")
        assert params == {}

    def test_single_param(self):
        router = self._make_router()
        params = router._log_params("mode=builds")
        assert params == {"mode": "builds"}

    def test_multiple_params(self):
        router = self._make_router()
        params = router._log_params("mode=install&name=8nime&action=build")
        assert params["mode"] == "install"
        assert params["name"] == "8nime"
        assert params["action"] == "build"

    def test_url_param(self):
        router = self._make_router()
        params = router._log_params("mode=youtube&url=https%3A%2F%2Fexample.com")
        assert params["mode"] == "youtube"
        assert "example.com" in params["url"]


class TestRouterDispatchModeExtraction:
    """Verify that mode/name/action/url are extracted correctly before dispatch."""

    def setup_method(self):
        from resources.libs.common.router import Router
        with patch("resources.libs.common.tools.ensure_folders"):
            self.router = Router()

    def _dispatch_captured(self, paramstring):
        """Call _log_params (pure parsing) and return the resulting params dict."""
        return self.router._log_params(paramstring)

    def test_mode_none_when_absent(self):
        params = self._dispatch_captured("")
        mode = params.get("mode")
        assert mode is None

    def test_mode_builds(self):
        params = self._dispatch_captured("mode=builds")
        assert params["mode"] == "builds"

    def test_mode_maint(self):
        params = self._dispatch_captured("mode=maint")
        assert params["mode"] == "maint"

    def test_mode_backup_with_action(self):
        params = self._dispatch_captured("mode=backup&action=backup")
        assert params["mode"] == "backup"
        assert params["action"] == "backup"

    def test_mode_restore_with_action(self):
        params = self._dispatch_captured("mode=restore&action=restore")
        assert params["mode"] == "restore"
        assert params["action"] == "restore"

    def test_mode_advanced_settings(self):
        params = self._dispatch_captured("mode=advanced_settings")
        assert params["mode"] == "advanced_settings"

    def test_mode_addons(self):
        params = self._dispatch_captured("mode=addons")
        assert params["mode"] == "addons"

    def test_all_four_params(self):
        params = self._dispatch_captured("mode=install&name=8nime&action=build&url=http://example.com")
        assert params["mode"] == "install"
        assert params["name"] == "8nime"
        assert params["action"] == "build"
        assert params["url"] == "http://example.com"


class TestRouterConstants:
    def test_addon_installer_mode_constant(self):
        from resources.libs.common import router
        assert router.addon_installer_mode == "addons"
