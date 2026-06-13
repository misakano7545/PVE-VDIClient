"""UI theme and font helpers."""

import customtkinter as ctk

from vdi.state import G

_font_cache = {}


def apply_theme():
	theme = str(G.theme).strip().lower() if G.theme else ''
	if 'dark' in theme:
		ctk.set_appearance_mode('Dark')
	elif 'light' in theme:
		ctk.set_appearance_mode('Light')
	else:
		ctk.set_appearance_mode('System')
	ctk.set_default_color_theme('blue')


def get_font(name):
	font_def = getattr(G, name, None)
	if isinstance(font_def, dict):
		if name not in _font_cache:
			_font_cache[name] = ctk.CTkFont(**font_def)
		return _font_cache[name]
	return font_def
