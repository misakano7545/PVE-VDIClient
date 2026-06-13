"""Modal popup dialogs."""

import customtkinter as ctk
import tkinter as tk

from vdi.i18n import t
from vdi.state import G
from vdi.ui.theme import get_font
from vdi.ui.window import VDIWindow, apply_kiosk_state, center_window, get_hidden_root


def win_popup(message):
	root = get_hidden_root()
	window = VDIWindow(root)
	window.overrideredirect(True)
	window.attributes("-topmost", True)
	window.protocol("WM_DELETE_WINDOW", lambda: None)

	frame = ctk.CTkFrame(window, corner_radius=12)
	frame.pack(padx=18, pady=18, fill='both', expand=True)
	label = ctk.CTkLabel(frame, text=message, wraplength=420, justify='center', font=get_font('LABEL_FONT'))
	label.pack(padx=10, pady=(10, 14))
	window.close = window.destroy
	center_window(window)
	window.lift()
	window.focus_force()
	window.update()
	return window


def win_popup_button(message, button=None):
	if button is None:
		button = t('common.ok')
	root = get_hidden_root()
	window = VDIWindow(root)
	window.title('')
	window.resizable(False, False)
	frame = ctk.CTkFrame(window, corner_radius=12)
	frame.pack(padx=18, pady=18, fill='both', expand=True)
	label = ctk.CTkLabel(frame, text=message, wraplength=420, justify='center', font=get_font('LABEL_FONT'))
	label.pack(padx=10, pady=(10, 14))

	def close_and_destroy():
		window.after(0, window.destroy)

	action = ctk.CTkButton(frame, text=button, command=close_and_destroy, font=get_font('BUTTON_FONT'))
	action.pack(padx=10, pady=(0, 10))
	center_window(window)
	apply_kiosk_state(window)
	window.lift()
	window.focus_force()
	if not G.kiosk:
		window.grab_set()
	try:
		window.wait_visibility(window)
	except tk.TclError:
		pass
	window.update()
	try:
		window.wait_window()
	except Exception:
		pass
