import re
from enum import Enum


class TraceField(Enum):
    """Enum for trace fields. DISASM, REGS, MEM, COMMENT or ANY"""
    DISASM = 0
    REGS = 1
    MEM = 2
    COMMENT = 3
    ANY = 4


def find(trace, field, keyword, start_row=0, direction=1):
    """Finds next/previous trace row with keyword

    Args:
        trace (list): Traced instructions, registers and memory (TraceData.trace)
        field (TraceField): Which field(s) to search
        keyword (str): Keyword to search for
        start_row (int): Trace row number to start search
        direction (int, optional): Search direction, 1 for forward, -1 for backward
            Defaults to 1.
    Returns:
        Trace row number, None if nothing found
    """
    if not keyword or not trace or start_row > len(trace):
        return None

    last_row = len(trace)

    if direction < 0:
        last_row = -1

    if field == TraceField.DISASM:
        keywords = keyword.split("/")
        for row in range(start_row, last_row, direction):
            disasm = trace[row]["disasm"]
            for key in keywords:
                if key in disasm:
                    return row

    elif field == TraceField.REGS:
        value = int(keyword, 16)
        for row in range(start_row, last_row, direction):
            if value in trace[row]["regs"]:
                return row

    elif field == TraceField.MEM:
        if keyword.startswith("0x"):
            keyword = int(keyword, 16)
        for row in range(start_row, last_row, direction):
            for mem in trace[row]["mem"]:
                if keyword in mem.values():
                    return row

    elif field == TraceField.COMMENT:
        for row in range(start_row, last_row, direction):
            if keyword in trace[row]["comment"]:
                return row

    elif field == TraceField.ANY:
        keyword_int = None
        if keyword.startswith("0x"):
            keyword_int = int(keyword, 16)

        for row in range(start_row, last_row, direction):
            if keyword in trace[row]["comment"]:
                return row
            for mem in trace[row]["mem"]:
                mem_values = mem.values()
                if keyword in mem_values:
                    return row
                if keyword_int and keyword_int in mem_values:
                    return row
            if keyword in trace[row]["disasm"]:
                return row
            if keyword_int and keyword_int in trace[row]["regs"]:
                return row

    else:
        print("Error in find. Unknown field.")

    return None


def filter_trace(trace, regs, filter_text):
    """Filters trace

    Args:
        trace (list): Traced instructions, registers and memory (TraceData.trace)
        filter_text (str): Filter text
        regs (dict): Register names and indexes (TraceData.regs)
    Returns:
        List of filtered trace records
    """
    data = trace
    filters = filter_text.split("/")
    if not filters or not data:
        return []
    value = ""

    for f in filters:
        f_parts = f.split("=")
        if len(f_parts) != 2 or not f_parts[1]:
            print("Error in filter.")
            break
        value = f_parts[1]
        if f_parts[0] == "rows":
            rows = value.split("-")
            start = int(rows[0])
            end = int(rows[1])
            data = data[start:end+1]
        elif f_parts[0] == "disasm":
            disasm_list = f_parts[1].split("|")
            data = list(filter(lambda x: any(k for k in disasm_list \
                if k in x["disasm"]), data))
        elif f_parts[0] == "opcodes":
            data = list(filter(lambda x: value in x["opcodes"], data))
        elif f_parts[0] == "comment":
            data = list(filter(lambda x: value in x["comment"], data))
        elif "reg_" in f_parts[0]:
            reg = f_parts[0].split("_")[1]
            value = int(value, 16)
            if reg == "any":
                data = list(filter(lambda x: value in x["regs"], data))
            elif data and reg in regs:
                reg_index = regs[reg]
                data = list(filter(lambda x: x["regs"][reg_index] == value, data))
            else:
                print("Error in filter, unknown register.")
                break
        elif f_parts[0] == "regex":
            data = list(filter(lambda x: re.search(value, str(x)) is not None, data))
        elif f_parts[0] == "iregex":
            data = list(filter(lambda x: re.search(value, str(x)) is None, data))
        elif f_parts[0] == "mem_value":
            value = int(value, 16)
            data = list(filter(lambda x: any(k for k in x["mem"] \
                        if k["value"] == value), data))
        elif f_parts[0] == "mem_read_value":
            value = int(value, 16)
            data = list(filter(lambda x: any(k for k in x["mem"] \
                        if k["value"] == value and k["access"] == "READ"), data))
        elif f_parts[0] == "mem_write_value":
            value = int(value, 16)
            data = list(filter(lambda x: any(k for k in x["mem"] \
                        if k["value"] == value and k["access"] == "WRITE"), data))
        elif f_parts[0] == "mem_addr":
            value = int(value, 16)
            data = list(filter(lambda x: any(k for k in x["mem"] \
                        if k["addr"] == value), data))
        elif f_parts[0] == "mem_read_addr":
            value = int(value, 16)
            data = list(filter(lambda x: any(k for k in x["mem"] \
                        if k["addr"] == value and k["access"] == "READ"), data))
        elif f_parts[0] == "mem_write_addr":
            value = int(value, 16)
            data = list(filter(lambda x: any(k for k in x["mem"] \
                        if k["addr"] == value and k["access"] == "WRITE"), data))
        else:
            print("Error. Unknown word in filter.")
            break
    return data
