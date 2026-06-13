#!/usr/bin/env python3
"""Proxmox VDI Client entry point."""

import sys

from vdi.main import main

if __name__ == '__main__':
	sys.exit(main())