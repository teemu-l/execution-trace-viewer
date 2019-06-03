from yapsy.IPlugin import IPlugin

class PluginPrintRows(IPlugin):

    def execute(self, main_window, trace_data, selected_row_ids):
        trace = trace_data.get_trace_rows(selected_row_ids)

        if not trace:
            print('PluginPrintRows error: Nothing selected.')
            return

        main_window.print('----------------------------------')

        row_id_digits = len(str(trace[-1]['id']))
        for t in trace:
            ip = hex(trace_data.get_instruction_pointer(t['id']))
            main_window.print(
                '{:<{}} '.format(t['id'], row_id_digits) +
                ' %s ' % ip +
                ' {:<42}'.format(t['disasm']) +
                '; %s' % t['comment']
            )
