# -*- coding: utf-8 -*-
"""Kodi 20+ dialog compatibility shim.

Kodi 19 removed the legacy multi-line ``line1, line2, line3`` arguments from
``xbmcgui.Dialog.ok()`` / ``yesno()`` and from
``xbmcgui.DialogProgress.create()`` / ``update()``; the signatures are now
``ok(heading, message)`` / ``yesno(heading, message, ...)`` /
``create(heading, message)`` / ``update(percent, message)``.

This wizard is an older fork with ~110 call sites using the old multi-line
form. Rather than rewrite each one, we subclass the dialogs to accept the
legacy calls (joining the extra positional arguments with newlines) and
monkeypatch ``xbmcgui`` so every ``xbmcgui.Dialog()`` /
``xbmcgui.DialogProgress()`` in the add-on transparently uses the compatible
versions. Import this module once, early (config.py does so).
"""
import xbmcgui

_BaseDialog = xbmcgui.Dialog
_BaseProgress = xbmcgui.DialogProgress


def _message(parts):
    return "\n".join(str(p) for p in parts if p not in (None, ""))


class _Dialog(_BaseDialog):
    def ok(self, heading, *lines, **kwargs):
        message = kwargs.pop("message", None)
        if message is None:
            message = _message(lines)
        return _BaseDialog.ok(self, heading, message)

    def yesno(self, heading, *lines, **kwargs):
        message = kwargs.pop("message", None)
        if message is None:
            message = _message(lines)
        # nolabel / yeslabel / autoclose / defaultbutton pass straight through
        return _BaseDialog.yesno(self, heading, message, **kwargs)


class _DialogProgress(_BaseProgress):
    def create(self, heading, *lines, **kwargs):
        message = kwargs.pop("message", None)
        if message is None:
            message = _message(lines)
        self._compat_message = message
        return _BaseProgress.create(self, heading, message)

    def update(self, percent, *lines, **kwargs):
        message = kwargs.pop("message", None)
        if message is None and lines:
            message = _message(lines)
        if message is None:
            # bare update(percent): keep the last message (old API behaviour)
            message = getattr(self, "_compat_message", "")
        else:
            self._compat_message = message
        return _BaseProgress.update(self, percent, message)


try:
    xbmcgui.Dialog = _Dialog
    xbmcgui.DialogProgress = _DialogProgress
except Exception:  # never let the shim break the add-on
    pass
