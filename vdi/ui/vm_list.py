"""VM selection list window."""

import math

import customtkinter as ctk

from vdi.i18n import t
from vdi.proxmox.vms import getvms, vmaction
from vdi.state import G
from vdi.ui.popups import win_popup_button
from vdi.ui.theme import get_font
from vdi.ui.window import (
	VDIWindow,
	apply_kiosk_state,
	get_hidden_root,
	load_image,
	set_window_icon,
)

_STATE_KEYS = {
	'stopped': 'state.stopped',
	'running': 'state.running',
	'starting': 'state.starting',
	'suspending': 'state.suspending',
	'suspended': 'state.suspended',
}


def _translate_state(state):
	key = _STATE_KEYS.get(state)
	if key:
		return t(key)
	return state


def _format_vm_state(state):
	return t('vm_list.state', state=_translate_state(state))


def _build_vm_row(parent, vm, on_connect, on_reset):
	frame = ctk.CTkFrame(parent, corner_radius=12)
	frame.pack(fill='x', padx=12, pady=(0, 10))
	info_frame = ctk.CTkFrame(frame, fg_color='transparent')
	info_frame.pack(side='left', fill='x', expand=True, padx=(0, 8))
	name_label = ctk.CTkLabel(info_frame, text=vm['name'], font=get_font('VM_NAME_FONT'))
	name_label.pack(anchor='w')
	state_label = ctk.CTkLabel(
		info_frame,
		text=t('vm_list.state', state=t('vm_list.state_unknown')),
		anchor='w',
		font=get_font('LABEL_FONT')
	)
	state_label.pack(anchor='w', pady=(4, 0))
	button_frame = ctk.CTkFrame(frame, fg_color='transparent')
	button_frame.pack(side='right')
	conn_button = ctk.CTkButton(button_frame, text=t('vm_list.connect'), width=120, command=lambda: on_connect(vm), font=get_font('BUTTON_FONT'))
	conn_button.pack(pady=(0, 4))
	reset_button = None
	if G.show_reset:
		reset_button = ctk.CTkButton(button_frame, text=t('vm_list.reset'), width=120, fg_color='#3b8ed0', hover_color='#4fa1e7', command=lambda: on_reset(vm), font=get_font('BUTTON_FONT'))
		reset_button.pack(pady=(0, 4))
	return frame, state_label, conn_button, reset_button


def showvms():
	vms = getvms()
	if vms is False:
		return False
	if len(vms) < 1:
		win_popup_button(t('vms.no_instances'))
		return False
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
	title_label.pack(pady=(0, 6))
	subtitle = ctk.CTkLabel(container, text=t('vm_list.select_desktop'), font=get_font('LABEL_FONT'))
	subtitle.pack(pady=(0, 14))
	ctk.CTkFrame(container, height=4, fg_color=("gray70", "gray30")).pack(fill='x', padx=10, pady=(0, 14))
	current_page = 0
	visible_vms = [vm for vm in vms if vm.get('status') != 'unknown']
	total_pages = max(1, math.ceil(len(visible_vms) / G.page_size))
	vm_frame = ctk.CTkFrame(container, fg_color='transparent')
	vm_frame.pack(fill='both', expand=True)
	page_frame = ctk.CTkFrame(container, fg_color='transparent')
	page_separator = ctk.CTkFrame(container, height=4, fg_color=("gray70", "gray30"))
	page_label = ctk.CTkLabel(page_frame, text=t('vm_list.page', current=current_page + 1, total=total_pages), font=get_font('LABEL_FONT'))
	prev_button = ctk.CTkButton(page_frame, text=t('vm_list.previous'), width=100, font=get_font('BUTTON_FONT'))
	next_button = ctk.CTkButton(page_frame, text=t('vm_list.next'), width=100, font=get_font('BUTTON_FONT'))
	vm_controls = {}
	current_vmlist = getvms(listonly=True)

	def update_vm_row(vm, state_label, conn_button):
		state = 'stopped'
		if vm.get('status') == 'running':
			if 'lock' in vm:
				state = vm['lock']
				if state in ('suspending', 'suspended'):
					if state == 'suspended':
						state = 'starting'
				conn_button.configure(state='disabled')
			else:
				state = vm['status']
				conn_button.configure(state='normal')
		else:
			conn_button.configure(state='normal')
		state_label.configure(text=_format_vm_state(state))

	def on_connect(vm):
		vmaction(vm['node'], vm['vmid'], vm['type'])

	def on_reset(vm):
		vmaction(vm['node'], vm['vmid'], vm['type'], action='reload')

	def update_page_controls():
		page_label.configure(text=t('vm_list.page', current=current_page + 1, total=total_pages))
		prev_button.configure(state='normal' if current_page > 0 else 'disabled')
		next_button.configure(state='normal' if current_page < total_pages - 1 else 'disabled')

	def change_page(delta):
		nonlocal current_page
		current_page = max(0, min(total_pages - 1, current_page + delta))
		update_page_controls()
		build_vm_list(visible_vms)

	prev_button.configure(command=lambda: change_page(-1))
	next_button.configure(command=lambda: change_page(1))

	def build_vm_list(vms_to_render):
		filtered_vms = [vm for vm in vms_to_render if vm.get('status') != 'unknown']
		nonlocal total_pages, current_page
		total_pages = max(1, math.ceil(len(filtered_vms) / G.page_size))
		current_page = min(current_page, total_pages - 1)
		start = current_page * G.page_size
		end = start + G.page_size
		page_items = filtered_vms[start:end]
		for child in vm_frame.winfo_children():
			child.destroy()
		vm_controls.clear()
		for i, vm in enumerate(page_items):
			frame, state_label, conn_button, reset_button = _build_vm_row(vm_frame, vm, on_connect, on_reset)
			update_vm_row(vm, state_label, conn_button)
			vm_controls[str(vm['vmid'])] = {
				'state': state_label,
				'button': conn_button
			}
			if i < len(page_items) - 1:
				ctk.CTkFrame(vm_frame, height=2, fg_color=("gray75", "gray25")).pack(fill='x', padx=24, pady=(0, 10))
		update_page_controls()
		if total_pages > 1:
			page_separator.pack(side='bottom', fill='x', pady=(10, 0))
			page_frame.pack(side='bottom', fill='x', pady=(4, 0))
			page_label.pack(side='left')
			prev_button.pack(side='left', padx=(10, 8))
			next_button.pack(side='left')
		else:
			page_separator.pack_forget()
			page_frame.pack_forget()

	refresh_id = None
	timeout_id = None

	def refresh():
		nonlocal current_vmlist, refresh_id

		new_list_only_vms = getvms(listonly=True)
		if new_list_only_vms is False:
			if window.winfo_exists():
				refresh_id = window.after(5000, refresh)
			return

		if new_list_only_vms != current_vmlist:
			current_vmlist = new_list_only_vms.copy()
			new_vms_full_details = getvms()
			if new_vms_full_details is False:
				if window.winfo_exists():
					refresh_id = window.after(5000, refresh)
				return
			if new_vms_full_details:
				build_vm_list(new_vms_full_details)
		else:
			new_vms_full_details = getvms()
			if new_vms_full_details is False:
				if window.winfo_exists():
					refresh_id = window.after(5000, refresh)
				return
			if new_vms_full_details:
				for vm in new_vms_full_details:
					row = vm_controls.get(str(vm['vmid']))
					if row:
						update_vm_row(vm, row['state'], row['button'])
		if window.winfo_exists():
			refresh_id = window.after(5000, refresh)

	def reset_timeout(event=None):
		nonlocal timeout_id
		if timeout_id:
			window.after_cancel(timeout_id)
		if G.timeout > 0:
			timeout_id = window.after(G.timeout * 60 * 1000, close_vm_window)

	def close_vm_window():
		nonlocal refresh_id, timeout_id
		if refresh_id and window.winfo_exists():
			window.after_cancel(refresh_id)
		if timeout_id and window.winfo_exists():
			window.after_cancel(timeout_id)
		result.update({'logout': True})
		window.destroy()

	logout_button = ctk.CTkButton(container, text=t('vm_list.logout'), fg_color='#d65f5f', hover_color='#d85f5f', command=close_vm_window, font=get_font('BUTTON_FONT'))
	logout_button.pack(side='bottom', pady=(12, 0), fill='x')

	build_vm_list(vms)

	window.update()
	width = window.winfo_reqwidth()
	height = window.winfo_reqheight()
	if G.width and G.height:
		try:
			requested_width = int(G.width)
			width = max(width, int(requested_width * 1.5))
		except Exception:
			pass
	x = max(0, (window.winfo_screenwidth() - width) // 2)
	y = max(0, (window.winfo_screenheight() - height) // 2)
	window.geometry(f"{width}x{height}+{x}+{y}")
	result = {'logout': False}
	window.protocol('WM_DELETE_WINDOW', close_vm_window)
	window.deiconify()
	apply_kiosk_state(window)
	if G.timeout > 0:
		reset_timeout()
		window.bind_all("<Any-KeyPress>", reset_timeout)
		window.bind_all("<Button>", reset_timeout)
		window.bind_all("<Motion>", reset_timeout)
	refresh_id = window.after(5000, refresh)
	window.wait_window()
	return not result['logout']
