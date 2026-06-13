"""Internationalization support."""

import json
import locale
import os
import sys

_FALLBACK = 'en'
_strings = {}
_current = _FALLBACK


def _locales_dir():
	if getattr(sys, 'frozen', False):
		return os.path.join(sys._MEIPASS, 'vdi', 'i18n', 'locales')
	return os.path.join(os.path.dirname(__file__), 'locales')


def _normalize(language):
	if not language:
		return None
	normalized = language.strip().replace('-', '_')
	lower = normalized.lower()
	if lower in ('zh', 'zh_cn', 'chinese', 'cn'):
		return 'zh_CN'
	if lower.startswith('zh'):
		return 'zh_CN'
	if lower in ('en', 'en_us', 'english'):
		return 'en'
	if lower.startswith('en'):
		return 'en'
	candidate = normalized if '_' in normalized else lower
	if os.path.isfile(os.path.join(_locales_dir(), f'{candidate}.json')):
		return candidate
	return None


def _load_locale(code):
	path = os.path.join(_locales_dir(), f'{code}.json')
	with open(path, encoding='utf-8') as handle:
		return json.load(handle)


def _detect_language():
	try:
		loc, _ = locale.getlocale(locale.LC_MESSAGES)
		if not loc:
			loc, _ = locale.getdefaultlocale()
		if loc and loc.lower().startswith('zh'):
			return 'zh_CN'
	except Exception:
		pass
	return 'zh_CN'


def init_i18n(language=None):
	global _strings, _current
	resolved = _normalize(language) or _detect_language()
	_current = resolved
	_strings = _load_locale(_FALLBACK)
	if resolved != _FALLBACK:
		_strings.update(_load_locale(resolved))


def set_language(language):
	init_i18n(language)


def get_language():
	return _current


def t(key, **kwargs):
	message = _strings.get(key, key)
	if kwargs:
		return message.format(**kwargs)
	return message
