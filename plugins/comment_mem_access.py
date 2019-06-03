"""This plugin finds every memory access and comments the row with mem address and value"""

from yapsy.IPlugin import IPlugin

class PluginCommentMemAccesses(IPlugin):

    def execute(self, main_window, trace_data, selected_row_ids):

        want_to_continue = main_window.ask_user(
            "Warning", "This plugin may replace some of your comments, continue?"
        )
        if not want_to_continue:
            return

        trace = main_window.get_visible_trace()

        for i, t in enumerate(trace):
            if 'mem' in t and t['mem']:
                comment = ""
                for mem in t['mem']:
                    addr = hex(mem['addr'])
                    value = hex(mem['value'])
                    if mem['access'] == "READ":
                        comment += f"[{ addr }] -> { value } "
                    elif mem['access'] == "WRITE":
                        comment += f"[{ addr }] <- { value } "
                trace[i]['comment'] = comment

        main_window.update_trace_table()
