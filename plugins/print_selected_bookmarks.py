"""This plugin prints all selected bookmarks from bookmarks table"""
from yapsy.IPlugin import IPlugin
from core.api import Api

class PluginPrintSelectedBookmarks(IPlugin):

    def execute(self, api: Api):

        api.print('')

        bookmarks = api.get_selected_bookmarks()

        for b in bookmarks:
            rows = "{:<13}".format(f"{b.startrow} - {b.endrow}")
            addr = "{:<12}".format(b.addr)
            disasm = "{:<20}".format(b.disasm)
            api.print(f"{rows}  {addr} {disasm} ; {b.comment}")
