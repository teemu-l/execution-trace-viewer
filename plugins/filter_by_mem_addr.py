"""This plugin demonstrates how to filter trace by memory range.
Every row which accesses memory between addr and addr+size
is added to filtered_trace.
"""

from yapsy.IPlugin import IPlugin
from core.api import Api

class PluginFilterByMemAddress(IPlugin):

    def execute(self, api: Api):

        addr_and_size = api.get_values_from_user(
            "Filter by memory address",
            "Give me memory address and size, separated by comma:"
        )

        if not addr_and_size or len(addr_and_size) != 2:
            print('Error. Wrong values given')
            return

        addr, size = addr_and_size

        api.print(f"Filtering by mem access addr: from {hex(addr)} to {hex(addr+size)}")

        trace = api.get_visible_trace()
        filtered_trace = []

        for t in trace:
            for mem in t['mem']:
                if addr <= mem['addr'] <= (addr + size):
                    filtered_trace.append(t.copy())
                    continue

        trace_len = len(filtered_trace)
        if trace_len > 0:
            api.print(f"Length of filtered trace: {trace_len}") 
            api.set_filtered_trace(filtered_trace)
            api.show_filtered_trace()
        else:
            api.print("Filter plugin resulted in empty trace")
