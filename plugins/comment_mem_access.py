"""This plugin finds every memory access and comments the row with address and value"""

from yapsy.IPlugin import IPlugin
from core.api import Api

class PluginCommentMemAccesses(IPlugin):

    def execute(self, api: Api):

        want_to_continue = api.ask_user(
            "Warning", "This plugin may replace some of your comments, continue?"
        )
        if not want_to_continue:
            return

        trace_data = api.get_trace_data()
        trace = api.get_visible_trace()

        for i, t in enumerate(trace):
            if 'mem' in t and t['mem']:
                comment = ""
                for mem in t['mem']:
                    addr = hex(mem['addr'])
                    value = mem['value']
                    if mem['access'] == "READ":
                        comment += f"[{ addr }] -> { hex(value) } "
                    elif mem['access'] == "WRITE":
                        comment += f"[{ addr }] <- { hex(value) } "
                    if 0x20 <= value <= 0x7e:
                        comment += f"'{ chr(value) }' "

                # Add comment to full trace
                row = t["id"]
                trace_data.trace[row]['comment'] = comment

                # Add comment to visible trace too because it could be filtered_trace
                trace[i]['comment'] = comment

        api.update_trace_table()
