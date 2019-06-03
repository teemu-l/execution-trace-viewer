"""This plugin demonstrates how to use find and add bookmarks"""

from yapsy.IPlugin import IPlugin

from core.bookmark import Bookmark
from core.filter_and_find import find
from core.filter_and_find import TraceField

class PluginFindMemWrites(IPlugin):

    def execute(self, main_window, trace_data, selected_row_ids):

        add_bookmarks = main_window.ask_user(
            "Add to bookmarks", "Add found writes to bookmarks?"
        )

        trace = main_window.get_visible_trace()
        trace_length = len(trace)
        main_window.print('Length of visible trace: %d' % trace_length)

        ip_reg_name = trace_data.get_instruction_pointer_name()
        ip_reg_index = trace_data.get_reg_index(ip_reg_name)
        row = 0

        while 1:
            row = find(
                trace=trace,
                field=TraceField.MEM,
                keyword='WRITE',
                start_row=row,
            )

            if row is None or row > trace_length:
                main_window.print('End of search')
                break

            address = hex(trace[row]['regs'][ip_reg_index])

            # convert all written values to hex string
            mems = []
            for mem in trace[row]['mem']:
                if mem['access'] == 'WRITE':
                    mems.append(mem)
            values = " ".join([hex(mem['value']) for mem in mems])

            bookmark = Bookmark(
                startrow=row,
                endrow=row,
                addr=address,
                disasm=trace[row]['disasm'],
                comment=values
            )

            main_window.print(
                f"mem write found at {row}, values: {values}"
            )

            if add_bookmarks:
                trace_data.add_bookmark(bookmark, replace=False)
            row += 1

        main_window.update_bookmark_table()
