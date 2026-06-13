"""Window utilities and base classes."""

import base64
import os
from io import BytesIO

import customtkinter as ctk
import tkinter as tk

from vdi.state import G


def _pil_resample():
	from PIL import Image
	if hasattr(Image, 'Resampling'):
		return Image.Resampling.LANCZOS
	return Image.ANTIALIAS


def _resize_image(image, size):
	return image.resize(size, _pil_resample())


class VDIWindow(ctk.CTkToplevel):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


def get_hidden_root():
	if getattr(G, '_hidden_root', None) is None:
		ctk.set_default_color_theme('blue')
		root = ctk.CTk()
		root.withdraw()
		G._hidden_root = root
	return G._hidden_root


def center_window(window):
	window.deiconify()
	window.update_idletasks()
	width = window.winfo_reqwidth()
	height = window.winfo_reqheight()
	screen_width = window.winfo_screenwidth()
	screen_height = window.winfo_screenheight()
	x = max(0, (screen_width - width) // 2)
	y = max(0, (screen_height - height) // 2)
	window.geometry(f"{width}x{height}+{x}+{y}")
	window.update()


def apply_kiosk_state(window):
	if G.kiosk:
		window.update()
		try:
			window.attributes('-type', 'toolbar')
		except tk.TclError:
			pass
		window.protocol("WM_DELETE_WINDOW", lambda: None)
		window.resizable(False, False)
		fixed_x = window.winfo_x()
		fixed_y = window.winfo_y()

		def lock_position(event):
			if not window.winfo_exists():
				return
			if window.winfo_x() != fixed_x or window.winfo_y() != fixed_y:
				window.geometry(f"+{fixed_x}+{fixed_y}")

		window.bind("<Configure>", lock_position, add="+")


def load_image(path, for_ctk_label=False, size=None):
	if not path or not os.path.exists(path):
		return None
	if for_ctk_label:
		try:
			from PIL import Image
			image = Image.open(path).convert("RGBA")
			if size:
				image = _resize_image(image, size)
			return ctk.CTkImage(light_image=image, dark_image=image, size=image.size if size is None else size)
		except Exception:
			try:
				return tk.PhotoImage(file=path)
			except Exception:
				if path.lower().endswith('.ico'):
					try:
						from PIL import Image
						image = Image.open(path).convert("RGBA")
						if size:
							image = _resize_image(image, size)
						buf = BytesIO()
						image.save(buf, format='PNG')
						data = base64.b64encode(buf.getvalue()).decode('ascii')
						return tk.PhotoImage(data=data)
					except Exception:
						return None
				return None
	try:
		return tk.PhotoImage(file=path)
	except Exception:
		if path.lower().endswith('.ico'):
			try:
				from PIL import Image
				image = Image.open(path).convert("RGBA")
				if size:
					image = _resize_image(image, size)
				buf = BytesIO()
				image.save(buf, format='PNG')
				data = base64.b64encode(buf.getvalue()).decode('ascii')
				return tk.PhotoImage(data=data)
			except Exception:
				return None
		return None


def set_window_icon(window):
	if not G.icon or not os.path.exists(G.icon):
		return

	def _apply_icon():
		try:
			if os.name == 'nt' and G.icon.lower().endswith('.ico'):
				window.wm_iconbitmap(G.icon)
			else:
				icon = load_image(G.icon)
				if icon:
					window.iconphoto(True, icon)
					window._icon_image = icon
		except Exception:
			pass

	window.after(200, _apply_icon)
