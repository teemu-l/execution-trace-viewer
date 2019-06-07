from yapsy.IPlugin import IPlugin

class PluginPrintRows(IPlugin):

    def execute(self, api):

        trace_data = api.get_trace_data()
        trace = api.get_selected_trace()

        if not trace:
            print('PluginPrintRows error: Nothing selected.')
            return

        api.print('----------------------------------')

        row_id_digits = len(str(trace[-1]['id']))
        for t in trace:
            ip = hex(trace_data.get_instruction_pointer(t['id']))
            api.print(
                '{:<{}} '.format(t['id'], row_id_digits) +
                ' %s ' % ip +
                ' {:<42}'.format(t['disasm']) +
                '; %s' % t['comment']
            )
