"""main.py: A calibre plugin containing an OPDS client"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015-2022"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

from calibre.customize import InterfaceActionBase

class OpdsClient(InterfaceActionBase):
    '''
    An OPDS client that can read the OPDS of a different calibre,
    and display the differences between this calibre and the other
    and download the missing books from the other calibre
    '''
    name = 'OPDS Client'
    description = 'Import from the OPDS catalog exported by a different calibre'
    supported_platforms = ['windows', 'osx', 'linux']
    author = "Steinar Bang"
    version = (1, 0, 0)
    minimum_calibre_version = (5, 0, 1)

    actual_plugin = 'calibre_plugins.opds_client.ui:OpdsInterfacePlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.opds_client.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()

        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
