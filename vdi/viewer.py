"""virt-viewer / remote-viewer command discovery."""

import os
import subprocess
import sys

from vdi.i18n import t
from vdi.state import G
from vdi.ui.popups import win_popup_button


def setcmd():
	try:
		if os.name == 'nt':  # Windows
			import csv
			cmd1 = 'ftype VirtViewer.vvfile'
			result = subprocess.check_output(cmd1, shell=True)
			cmdresult = result.decode('utf-8')
			cmdparts = cmdresult.split('=')
			for row in csv.reader([cmdparts[1]], delimiter=' ', quotechar='"'):
				G.vvcmd = row[0]
				break

		elif os.name == 'posix':
			subprocess.check_output('which remote-viewer', shell=True)
			G.vvcmd = 'remote-viewer'
	except subprocess.CalledProcessError:
		if os.name == 'nt':
			win_popup_button(t('viewer.missing_windows'))
		elif os.name == 'posix':
			win_popup_button(t('viewer.missing_linux'))
		sys.exit()
