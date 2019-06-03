from yapsy.IPlugin import IPlugin
from operator import itemgetter

class PluginPrintExecCounts(IPlugin):

    def execute(self, main_window, trace_data, selected_row_ids):

        main_window.print('----------------------------------')
        trace = main_window.get_visible_trace()
        if not trace:
            return

        ip_name = trace_data.get_instruction_pointer_name()
        if ip_name not in trace_data.regs:
            main_window.print('Error. Unknown instruction pointer name.')
            return
        ip_index = trace_data.regs[ip_name]
        counts = {}
        for t in trace:
            addr = t['regs'][ip_index]
            if addr in counts:
                counts[addr] += 1
            else:
                counts[addr] = 1

        main_window.print('%d unique addresses executed.' % len(counts))
        main_window.print('Top 30 executed addresses:')

        counts = sorted(counts.items(), key=itemgetter(1), reverse=True)
        for address, count in counts[:30]:
            main_window.print('%s  %d ' % (hex(address), count))
