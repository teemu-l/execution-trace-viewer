"""This plugin prints all selected bookmarks from bookmarks table"""
from yapsy.IPlugin import IPlugin
from operator import itemgetter

class PluginPrintSelectedBookmarks(IPlugin):

    def execute(self, api):

        api.print('')

        bookmarks = api.get_selected_bookmarks()
        if not bookmarks:
            return

        for b in bookmarks:
            startrow = '{:<8}'.format(b.startrow)
            endrow = '{:<8}'.format(b.endrow)
            addr = '{:<14}'.format(b.addr)
            disasm = '{:<20}'.format(b.disasm)
            api.print(f"{startrow} {endrow} {addr} {disasm} ; {b.comment}")

        api.print('')
