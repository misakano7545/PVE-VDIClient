"""Application entry point and main loop."""

import sys

if sys.platform == 'win32' and sys.getwindowsversion().major == 6 and sys.getwindowsversion().minor == 1:
	import customtkinter
	customtkinter.deactivate_automatic_dpi_awareness()

import argparse

from vdi.config import loadconfig
from vdi.i18n import init_i18n, t
from vdi.proxmox.vms import getvms, vmaction
from vdi.state import G
from vdi.ui.login import loginwindow
from vdi.ui.popups import win_popup_button
from vdi.ui.theme import apply_theme
from vdi.ui.vm_list import showvms
from vdi.viewer import setcmd


def main():
	G.scaling = 1  # TKinter requires integers
	parser = argparse.ArgumentParser(description='Proxmox VDI Client')
	parser.add_argument('--list_themes', help='List all available themes', action='store_true')
	parser.add_argument('--config_type', help='Select config type (default: file)', choices=['file', 'http'], default='file')
	parser.add_argument('--config_location', help='Specify the config location (default: search for config file)', default=None)
	parser.add_argument('--config_username', help="HTTP basic authentication username (default: None)", default=None)
	parser.add_argument('--config_password', help="HTTP basic authentication password (default: None)", default=None)
	parser.add_argument('--ignore_ssl', help="HTTPS ignore SSL certificate errors (default: False)", action='store_false', default=True)
	parser.add_argument('--language', help='UI language (e.g. zh_CN, en; default: auto-detect)', default=None)
	args = parser.parse_args()
	init_i18n(args.language)
	if args.list_themes:
		print(t('cli.appearance_modes'))
		print(t('cli.default_color_theme'))
		return
	setcmd()
	if not loadconfig(config_location=args.config_location, config_type=args.config_type, config_username=args.config_username, config_password=args.config_password, ssl_verify=args.ignore_ssl):
		return False
	apply_theme()
	loggedin = False
	switching = False
	while True:
		if not loggedin:
			loggedin, switching = loginwindow()
			if not loggedin and not switching:
				if G.hosts[G.current_hostset]['user'] and G.hosts[G.current_hostset]['token_name'] and G.hosts[G.current_hostset]['token_value']:
					return 1
				break
			elif not loggedin and switching:
				pass
			else:
				if G.hosts[G.current_hostset]['auto_vmid']:
					vms = getvms()
					for row in vms:
						if row['vmid'] == G.hosts[G.current_hostset]['auto_vmid']:
							vmaction(row['node'], row['vmid'], row['type'], action='connect')
							return 0
					win_popup_button(t('main.auto_vmid_not_found', vmid=G.hosts[G.current_hostset]['auto_vmid']))
				vmstat = showvms()
				if not vmstat:
					G.proxmox = None
					loggedin = False
					if G.hosts[G.current_hostset]['user'] and G.hosts[G.current_hostset]['token_name'] and G.hosts[G.current_hostset]['token_value'] and len(G.hosts) == 1:
						return 0
				else:
					return
