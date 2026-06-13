#!/usr/bin/env python3
"""Write dist/*.json metadata for MSI packaging."""

import argparse
import json
import os
from pathlib import Path

COMMON = {
	'manufacturer': 'Josh Patten',
	'arch': 64,
	'installdir': 'VDIClient',
	'installscope': 'perMachine',
	'license_file': 'License.rtf',
	'startmenu_shortcut': 'vdiclient.exe',
	'desktop_shortcut': 'vdiclient.exe',
	'parts': [
		{
			'id': 'MainProgram',
			'title': 'VDI Client',
			'description': 'Proxmox VDI Client',
			'absent': 'disallow',
			'staged_dir': 'vdiclient',
		}
	],
	'major_upgrade': {
		'Schedule': 'afterInstallInitialize',
		'AllowSameVersionUpgrades': 'yes',
	},
	'languages': [
		{'culture': 'en-us', 'lcid': 1033, 'codepage': 1252},
		{'culture': 'zh-cn', 'lcid': 2052, 'codepage': 936},
	],
}

VARIANTS = {
	'default': {
		'upgrade_guid': '46cbad92-353e-4b28-9bee-83950991dad8',
		'product_name': 'VDI Client',
		'name': 'VDI Client',
		'name_base': 'vdiclient',
		'comments': (
			'This is the Proxmox VDI client. '
			'This client interfaces with Proxmox requires that virt-viewer be installed.'
		),
		'output': 'dist/vdiclient.json',
	},
	'win7': {
		'upgrade_guid': 'f7e8d9c0-b1a2-4c3d-8e7f-6a5b4c3d2e1f',
		'product_name': 'VDI Client (Windows 7)',
		'name': 'VDI Client (Windows 7)',
		'name_base': 'vdiclient-win7',
		'comments': (
			'Legacy Proxmox VDI client build for Windows 7 SP1 (64-bit). '
			'Requires virt-viewer, KB2533623, and TLS 1.2 updates.'
		),
		'output': 'dist/vdiclient-win7.json',
	},
}


def main():
	parser = argparse.ArgumentParser(description='Write MSI package metadata JSON.')
	parser.add_argument(
		'--variant',
		choices=sorted(VARIANTS),
		default='default',
		help='Package variant (default: default)',
	)
	parser.add_argument(
		'--version',
		default=os.environ.get('MSI_VERSION', '0.0.0.0'),
		help='Four-part MSI version (default: MSI_VERSION env or 0.0.0.0)',
	)
	args = parser.parse_args()

	variant = VARIANTS[args.variant]
	metadata = {**COMMON, **{k: v for k, v in variant.items() if k != 'output'}}
	metadata['version'] = args.version

	output = Path(variant['output'])
	output.parent.mkdir(parents=True, exist_ok=True)
	output.write_text(json.dumps(metadata, indent='\t') + '\n', encoding='utf-8')
	print(f'Wrote {output}')


if __name__ == '__main__':
	main()
