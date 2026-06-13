"""Proxmox VE authentication."""

import random

import proxmoxer
import requests

from vdi.state import G


def pveauth(username, passwd=None, totp=None):
	random.shuffle(G.hosts[G.current_hostset]['hostpool'])
	err = None
	for hostinfo in G.hosts[G.current_hostset]['hostpool']:
		host = hostinfo['host']
		if 'port' in hostinfo:
			port = hostinfo['port']
		else:
			port = 8006
		connected = False
		authenticated = False
		if not connected and not authenticated:
			try:
				if G.hosts[G.current_hostset]['token_name'] and G.hosts[G.current_hostset]['token_value']:
					G.proxmox = proxmoxer.ProxmoxAPI(
						host,
						user=f"{username}@{G.hosts[G.current_hostset]['backend']}",
						token_name=G.hosts[G.current_hostset]['token_name'],
						token_value=G.hosts[G.current_hostset]['token_value'],
						verify_ssl=G.hosts[G.current_hostset]['verify_ssl'],
						port=port
					)
				elif totp:
					G.proxmox = proxmoxer.ProxmoxAPI(
						host,
						user=f"{username}@{G.hosts[G.current_hostset]['backend']}",
						otp=totp,
						password=passwd,
						verify_ssl=G.hosts[G.current_hostset]['verify_ssl'],
						port=port
					)
				else:
					G.proxmox = proxmoxer.ProxmoxAPI(
						host,
						user=f"{username}@{G.hosts[G.current_hostset]['backend']}",
						password=passwd,
						verify_ssl=G.hosts[G.current_hostset]['verify_ssl'],
						port=port
					)
				connected = True
				authenticated = True
				return connected, authenticated, err
			except proxmoxer.backends.https.AuthenticationError as e:
				err = e
				connected = True
				return connected, authenticated, err
			except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
				err = e
				connected = False
	return connected, authenticated, err
