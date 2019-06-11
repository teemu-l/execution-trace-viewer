"""This plugin prints top 30 most executed addresses"""
from yapsy.IPlugin import IPlugin
from operator import itemgetter
from core.api import Api

class PluginPrintExecCounts(IPlugin):

    def execute(self, api: Api):

        trace = api.get_visible_trace()
        if not trace:
            return

        api.print('')

        trace_data = api.get_trace_data()
        ip_name = trace_data.get_instruction_pointer_name()
        if ip_name not in trace_data.regs:
            api.print('Error. Unknown instruction pointer name.')
            return
        ip_index = trace_data.regs[ip_name]
        counts = {}
        for t in trace:
            addr = t['regs'][ip_index]
            if addr in counts:
                counts[addr] += 1
            else:
                counts[addr] = 1

        api.print('%d unique addresses executed.' % len(counts))
        api.print('Top 30 executed addresses:')

        counts = sorted(counts.items(), key=itemgetter(1), reverse=True)
        for address, count in counts[:30]:
            api.print('%s  %d ' % (hex(address), count))
