"""Application-wide shared state."""


class G:
	spiceproxy_conv = {}
	proxmox = None
	icon = None
	vvcmd = None
	scaling = 1
	#########
	inidebug = False
	addl_params = None
	imagefile = None
	kiosk = False
	viewer_kiosk = True
	fullscreen = True
	show_reset = False
	show_hibernate = False
	current_hostset = 'DEFAULT'
	title = None
	language = None
	hosts = {}
	theme = 'LightBlue'
	guest_type = 'both'
	width = None
	height = None
	page_size = 10
	timeout = 15
	TITLE_FONT = {'size': 30, 'weight': 'bold'}
	VM_NAME_FONT = {'size': 24, 'weight': 'bold'}
	DEFAULT_FONT = {'size': 18}
	LABEL_FONT = {'size': 18}
	BUTTON_FONT = {'size': 18}
