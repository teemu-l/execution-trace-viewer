"""This plugin filters a trace by addresses in memory accesses.
Every row which accesses memory in given range is added to filtered_trace.
"""

from yapsy.IPlugin import IPlugin
from core.api import Api


class PluginFilterByMemAddress(IPlugin):
    def execute(self, api: Api):

        input_dlg_data = [
            {"label": "Memory address", "data": "0x0"},
            {"label": "Size", "data": 2000},
            {"label": "Access types", "data": ["Reads and writes", "Reads", "Writes"]},
            {"label": "Source trace", "data": ["Full trace", "Filtered trace"]},
        ]
        options = api.get_values_from_user("Filter by memory address", input_dlg_data)

        if not options:
            return

        addr, size, access_types, trace_id = options
        addr = self.str_to_int(addr)

        print(f"Filtering by mem address: from {hex(addr)} to {hex(addr+size)}")

        if trace_id == 0:
            trace = api.get_full_trace()
        else:
            trace = api.get_filtered_trace()

        result_trace = []

        for t in trace:
            for mem in t["mem"]:
                if mem["access"].upper() == "READ" and access_types == 2:
                    continue
                elif mem["access"].upper() == "WRITE" and access_types == 1:
                    continue
                if addr <= mem["addr"] <= (addr + size):
                    result_trace.append(t.copy())
                    break  # avoid adding the same row more than once

        if len(result_trace) > 0:
            print(f"Length of filtered trace: {len(result_trace)}")
            api.set_filtered_trace(result_trace)
            api.show_filtered_trace()
        else:
            api.show_messagebox(
                "Error", "Could not find any rows accessing given memory area"
            )

    def str_to_int(self, s: str):
        result = 0
        if s:
            s = s.strip()
            if "0x" in s:
                result = int(s, 16)
            else:
                result = int(s)
        return result
