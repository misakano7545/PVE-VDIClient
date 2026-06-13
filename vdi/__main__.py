"""Allow running as python -m vdi."""

from vdi.main import main

if __name__ == '__main__':
	import sys
	sys.exit(main())
