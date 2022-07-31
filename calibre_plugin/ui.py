"""main.py: GUI initialization for a Calibre plugin implementing an OPDS client"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015-2022"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.opds_client.main import OpdsDialog

class OpdsInterfacePlugin(InterfaceAction):
    name = 'OPDS Client Interface plugin'

    action_spec = ('OPDS Client', None, 'Run the OPDS client UI', 'Ctrl+Shift+F1')

    def genesis(self):
        icon = get_icons('image/opds_client_icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config
        d = OpdsDialog(self.gui, self.qaction.icon(), do_user_config)
        d.show()

    def apply_settings(self):
        from config import prefs
        prefs

