"""Login window."""

import subprocess

import customtkinter as ctk

from vdi.i18n import t
from vdi.proxmox.auth import pveauth
from vdi.state import G
from vdi.ui.popups import win_popup, win_popup_button
from vdi.ui.theme import get_font
from vdi.ui.window import (
	VDIWindow,
	apply_kiosk_state,
	get_hidden_root,
	load_image,
	set_window_icon,
)


def _build_login_window():
	root = get_hidden_root()
	window = VDIWindow(root)
	window.title(G.title)
	set_window_icon(window)
	container = ctk.CTkFrame(window, corner_radius=15)
	container.pack(padx=20, pady=20, fill='both', expand=True)
	if G.imagefile:
		image = load_image(G.imagefile, for_ctk_label=True)
		if image:
			logo = ctk.CTkLabel(container, image=image, text='', fg_color='transparent')
			logo.image = image
			logo.pack(pady=(0, 12))
	title_label = ctk.CTkLabel(container, text=G.title, font=get_font('TITLE_FONT'))
	title_label.pack(pady=(0, 16))
	group_combo = None
	if len(G.hosts) > 1:
		groups = list(G.hosts.keys())
		combo_label = ctk.CTkLabel(container, text=t('login.server_group'), font=get_font('LABEL_FONT'))
		combo_label.pack(anchor='w', pady=(0, 4))
		group_combo = ctk.CTkComboBox(container, values=groups, font=get_font('DEFAULT_FONT'))
		group_combo.set(G.current_hostset)
		group_combo.pack(fill='x', pady=(0, 14))
	username_label = ctk.CTkLabel(container, text=t('login.username'), font=get_font('LABEL_FONT'))
	username_label.pack(anchor='w', pady=(0, 4))
	username_entry = ctk.CTkEntry(container, placeholder_text=t('login.username'), font=get_font('DEFAULT_FONT'))
	username_entry.insert(0, G.hosts[G.current_hostset]['user'] or '')
	username_entry.pack(fill='x', pady=(0, 12))
	username_entry.focus_set()
	password_label = ctk.CTkLabel(container, text=t('login.password'), font=get_font('LABEL_FONT'))
	password_label.pack(anchor='w', pady=(0, 4))
	password_entry = ctk.CTkEntry(container, placeholder_text=t('login.password'), show='*', font=get_font('DEFAULT_FONT'))
	password_entry.pack(fill='x', pady=(0, 12))
	totp_entry = None
	if G.hosts[G.current_hostset]['totp']:
		totp_label = ctk.CTkLabel(container, text=t('login.otp_key'), font=get_font('LABEL_FONT'))
		totp_label.pack(anchor='w', pady=(0, 4))
		totp_entry = ctk.CTkEntry(container, placeholder_text=t('login.totp_placeholder'), font=get_font('DEFAULT_FONT'))
		totp_entry.pack(fill='x', pady=(0, 12))
	button_frame = ctk.CTkFrame(container, fg_color='transparent')
	button_frame.pack(fill='x', pady=(6, 0))
	login_button = ctk.CTkButton(button_frame, text=t('login.log_in'), font=get_font('BUTTON_FONT'))
	login_button.pack(side='left', expand=True, fill='x', padx=(0, 8 if not G.kiosk else 0))
	cancel_button = None
	if not G.kiosk:
		cancel_button = ctk.CTkButton(button_frame, text=t('login.cancel'), font=get_font('BUTTON_FONT'))
		cancel_button.pack(side='left', expand=True, fill='x')
	pwreset_button = None
	if G.hosts[G.current_hostset]['pwresetcmd']:
		pwreset_button = ctk.CTkButton(container, text=t('login.password_reset'), font=get_font('BUTTON_FONT'))
		pwreset_button.pack(fill='x', pady=(12, 0))
	window.update()
	width = window.winfo_reqwidth()
	height = window.winfo_reqheight()
	x = max(0, (window.winfo_screenwidth() - width) // 2)
	y = max(0, (window.winfo_screenheight() - height) // 2)
	window.geometry(f"{width}x{height}+{x}+{y}")
	window.deiconify()
	apply_kiosk_state(window)
	username_entry.focus_set()
	return {
		'window': window,
		'group_combo': group_combo,
		'username_entry': username_entry,
		'password_entry': password_entry,
		'totp_entry': totp_entry,
		'login_button': login_button,
		'cancel_button': cancel_button,
		'pwreset_button': pwreset_button
	}


def loginwindow():
	if G.hosts[G.current_hostset]['user'] and G.hosts[G.current_hostset]['token_name'] and G.hosts[G.current_hostset]['token_value'] and len(G.hosts) == 1:
		popwin = win_popup(t('login.authenticating'))
		connected, authenticated, error = pveauth(G.hosts[G.current_hostset]['user'])
		popwin.close()
		if not connected:
			win_popup_button(t('login.connection_failed', error=error))
			return False, False
		elif connected and not authenticated:
			win_popup_button(t('login.invalid_credentials'))
			return False, False
		elif connected and authenticated:
			return True, False
	window_data = _build_login_window()
	window = window_data['window']
	result = {'action': None, 'group': None}

	def on_switch(choice):
		if choice and choice != G.current_hostset:
			result['action'] = 'switch'
			result['group'] = choice
			window.destroy()

	def do_cancel():
		result['action'] = 'cancel'
		window.destroy()

	def do_login():
		user = window_data['username_entry'].get()
		passwd = window_data['password_entry'].get()
		totp = None
		if window_data['totp_entry']:
			totp = window_data['totp_entry'].get()
		popwin = win_popup(t('login.authenticating'))
		connected, authenticated, error = pveauth(user, passwd=passwd, totp=totp)
		popwin.close()
		if not connected:
			win_popup_button(t('login.connection_failed', error=error))
		elif connected and not authenticated:
			win_popup_button(t('login.invalid_credentials'))
		else:
			result['action'] = 'login'
			window.destroy()

	if window_data['group_combo']:
		window_data['group_combo'].configure(command=on_switch)
	window_data['login_button'].configure(command=do_login)
	if window_data['cancel_button']:
		window_data['cancel_button'].configure(command=do_cancel)
	if window_data['pwreset_button']:
		def open_reset():
			try:
				subprocess.check_call(G.hosts[G.current_hostset]['pwresetcmd'], shell=True)
			except Exception as e:
				win_popup_button(t('login.password_reset_failed', error=e))
		window_data['pwreset_button'].configure(command=open_reset)
	window.bind('<Return>', lambda event: do_login())
	window.protocol('WM_DELETE_WINDOW', do_cancel)
	if not G.kiosk:
		window.grab_set()
	window.wait_window()

	if result['action'] == 'switch':
		G.current_hostset = result['group']
		return False, True
	if result['action'] == 'login':
		return True, False
	return False, False
