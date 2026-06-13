"""INI debug viewer window."""

import customtkinter as ctk

from vdi.i18n import t
from vdi.state import G
from vdi.ui.theme import get_font
from vdi.ui.window import VDIWindow, apply_kiosk_state, get_hidden_root, set_window_icon


def iniwin(inistring):
	root = get_hidden_root()
	window = VDIWindow(root)
	window.title(t('debug.title'))
	set_window_icon(window)
	window.geometry('850x550')
	text_box = ctk.CTkTextbox(window, width=820, height=460, corner_radius=10, font=get_font('DEFAULT_FONT'))
	text_box.pack(padx=15, pady=(15, 8), fill='both', expand=True)
	text_box.insert('0.0', inistring)
	text_box.configure(state='disabled')
	close_btn = ctk.CTkButton(window, text=t('common.close'), command=window.destroy, font=get_font('BUTTON_FONT'))
	close_btn.pack(pady=(0, 15))
	if not G.kiosk:
		window.grab_set()
	apply_kiosk_state(window)
	window.wait_window()
	return True
