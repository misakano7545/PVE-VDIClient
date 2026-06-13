"""Configuration file loading."""

import json
import os
from configparser import ConfigParser

import requests

from vdi.i18n import set_language, t
from vdi.state import G
from vdi.ui.popups import win_popup_button


def loadconfig(config_location=None, config_type='file', config_username=None, config_password=None, ssl_verify=True):
	config = ConfigParser(delimiters='=')
	if config_type == 'file':
		if config_location:
			if not os.path.isfile(config_location):
				win_popup_button(t('config.file_not_found', path=config_location))
				return False
		else:
			if os.name == 'nt':  # Windows
				config_list = [
					f'{os.getenv("APPDATA")}\\VDIClient\\vdiclient.ini',
					f'{os.getenv("PROGRAMFILES")}\\VDIClient\\vdiclient.ini',
					f'{os.getenv("PROGRAMFILES(x86)")}\\VDIClient\\vdiclient.ini',
					'C:\\Program Files\\VDIClient\\vdiclient.ini'
				]

			elif os.name == 'posix':  # Linux
				config_list = [
					os.path.expanduser('~/.config/VDIClient/vdiclient.ini'),
					'/etc/vdiclient/vdiclient.ini',
					'/usr/local/etc/vdiclient/vdiclient.ini'
				]
			for location in config_list:
				if os.path.exists(location):
					config_location = location
					break
			if not config_location:
				win_popup_button(t('config.not_found_anywhere'))
				return False
		try:
			config.read(config_location)
		except Exception as e:
			win_popup_button(t('config.read_error', error=repr(e)))
			return False
	elif config_type == 'http':
		if not config_location:
			win_popup_button(t('config.http_no_url'))
			return False
		try:
			if config_username and config_password:
				r = requests.get(url=config_location, auth=(config_username, config_password), verify=ssl_verify)
			else:
				r = requests.get(url=config_location, verify=ssl_verify)
			config.read_string(r.text)
		except Exception as e:
			win_popup_button(t('config.http_read_error', error=e))
			return False
	if 'General' not in config:
		win_popup_button(t('config.no_general_section'))
		return False
	else:
		if 'language' in config['General']:
			set_language(config['General']['language'])
			G.language = config['General']['language']
		if 'title' in config['General']:
			G.title = config['General']['title']
		else:
			G.title = t('app.default_title')
		if 'theme' in config['General']:
			G.theme = config['General']['theme']
		if 'icon' in config['General']:
			if os.path.exists(config['General']['icon']):
				G.icon = config['General']['icon']
		if 'logo' in config['General']:
			if os.path.exists(config['General']['logo']):
				G.imagefile = config['General']['logo']
		if 'kiosk' in config['General']:
			G.kiosk = config['General'].getboolean('kiosk')
		if 'viewer_kiosk' in config['General']:
			G.viewer_kiosk = config['General'].getboolean('viewer_kiosk')
		if 'fullscreen' in config['General']:
			G.fullscreen = config['General'].getboolean('fullscreen')
		if 'inidebug' in config['General']:
			G.inidebug = config['General'].getboolean('inidebug')
		if 'guest_type' in config['General']:
			G.guest_type = config['General']['guest_type']
		if 'show_reset' in config['General']:
			G.show_reset = config['General'].getboolean('show_reset')
		if 'window_width' in config['General']:
			G.width = config['General'].getint('window_width')
		if 'window_height' in config['General']:
			G.height = config['General'].getint('window_height')
		if 'page_size' in config['General']:
			G.page_size = config['General'].getint('page_size')
		if 'timeout' in config['General']:
			G.timeout = config['General'].getint('timeout')

	if 'Authentication' in config:  # Legacy configuration
		G.hosts['DEFAULT'] = {
			'hostpool': [],
			'backend': 'pve',
			'user': "",
			'token_name': None,
			'token_value': None,
			'totp': False,
			'verify_ssl': True,
			'pwresetcmd': None,
			'auto_vmid': None,
			'knock_seq': []
		}
		if 'Hosts' not in config:
			win_popup_button(t('config.no_hosts_section'))
			return False
		for key in config['Hosts']:
			G.hosts['DEFAULT']['hostpool'].append({
				'host': key,
				'port': int(config['Hosts'][key])
			})
		if 'auth_backend' in config['Authentication']:
			G.hosts['DEFAULT']['backend'] = config['Authentication']['auth_backend']
		if 'user' in config['Authentication']:
			G.hosts['DEFAULT']['user'] = config['Authentication']['user']
		if 'token_name' in config['Authentication']:
			G.hosts['DEFAULT']['token_name'] = config['Authentication']['token_name']
		if 'token_value' in config['Authentication']:
			G.hosts['DEFAULT']['token_value'] = config['Authentication']['token_value']
		if 'auth_totp' in config['Authentication']:
			G.hosts['DEFAULT']['totp'] = config['Authentication'].getboolean('auth_totp')
		if 'tls_verify' in config['Authentication']:
			G.hosts['DEFAULT']['verify_ssl'] = config['Authentication'].getboolean('tls_verify')
		if 'pwresetcmd' in config['Authentication']:
			G.hosts['DEFAULT']['pwresetcmd'] = config['Authentication']['pwresetcmd']
		if 'auto_vmid' in config['Authentication']:
			G.hosts['DEFAULT']['auto_vmid'] = config['Authentication'].getint('auto_vmid')
		if 'knock_seq' in config['Authentication']:
			try:
				G.hosts['DEFAULT']['knock_seq'] = json.loads(config['Authentication']['knock_seq'])
			except Exception as e:
				win_popup_button(t('config.knock_invalid_json', error=repr(e)))
	else:  # New style config
		i = 0
		for section in config.sections():
			if section.startswith('Hosts.'):
				_, group = section.split('.', 1)
				if i == 0:
					G.current_hostset = group
				G.hosts[group] = {
					'hostpool': [],
					'backend': 'pve',
					'user': "",
					'token_name': None,
					'token_value': None,
					'totp': False,
					'verify_ssl': True,
					'pwresetcmd': None,
					'auto_vmid': None,
					'knock_seq': []
				}
				try:
					hostjson = json.loads(config[section]['hostpool'])
				except Exception as e:
					win_popup_button(t('config.hostpool_parse_error', section=section, error=repr(e)))
					return False
				for key, value in hostjson.items():
					G.hosts[group]['hostpool'].append({
						'host': key,
						'port': int(value)
					})
				if 'auth_backend' in config[section]:
					G.hosts[group]['backend'] = config[section]['auth_backend']
				if 'user' in config[section]:
					G.hosts[group]['user'] = config[section]['user']
				if 'token_name' in config[section]:
					G.hosts[group]['token_name'] = config[section]['token_name']
				if 'token_value' in config[section]:
					G.hosts[group]['token_value'] = config[section]['token_value']
				if 'auth_totp' in config[section]:
					G.hosts[group]['totp'] = config[section].getboolean('auth_totp')
				if 'tls_verify' in config[section]:
					G.hosts[group]['verify_ssl'] = config[section].getboolean('tls_verify')
				if 'pwresetcmd' in config[section]:
					G.hosts[group]['pwresetcmd'] = config[section]['pwresetcmd']
				if 'auto_vmid' in config[section]:
					G.hosts[group]['auto_vmid'] = config[section].getint('auto_vmid')
				if 'knock_seq' in config[section]:
					try:
						G.hosts[group]['knock_seq'] = json.loads(config[section]['knock_seq'])
					except Exception as e:
						win_popup_button(t('config.knock_invalid_json', error=repr(e)))
				i += 1
	if 'SpiceProxyRedirect' in config:
		for key in config['SpiceProxyRedirect']:
			G.spiceproxy_conv[key] = config['SpiceProxyRedirect'][key]
	if 'AdditionalParameters' in config:
		G.addl_params = {}
		for key in config['AdditionalParameters']:
			G.addl_params[key] = config['AdditionalParameters'][key]
	return True
