import json
import traceback
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_MODE_64

from core.trace_data import TraceData
from core.bookmark import Bookmark
from core import prefs


def open_trace(filename):
    """Opens trace file and reads trace data and bookmarks

    Args:
        filename: name of trace file
    """
    try:
        with open(filename, "rb") as f:
            magic = f.read(4)
    except IOError:
        print("Error, could not open file.")
    else:
        if magic == b"TRAC":
            return open_x64dbg_trace(filename)
        elif magic == b"TVTR":
            return open_tv_trace(filename)
        return open_json_trace(filename)
    return None


def open_tv_trace(filename):
    """Opens tvt trace file and reads trace data and bookmarks

    Args:
        filename: name of trace file
    """
    with open(filename, "rb") as f:
        trace_data = TraceData()
        trace_data.filename = filename

        # check first 4 bytes
        magic = f.read(4)
        if magic != b"TVTR":
            raise ValueError("Error, wrong file format.")

        json_length_bytes = f.read(4)
        json_length = int.from_bytes(json_length_bytes, "little")

        # read JSON blob
        json_blob = f.read(json_length)
        json_str = str(json_blob, "utf-8")
        file_info = json.loads(json_str)

        arch = file_info.get("arch", "")

        reg_indexes = {}
        if arch == "x64":
            regs = prefs.X64_REGS
            for i, reg in enumerate(regs):
                reg_indexes[reg] = i
            pointer_size = 8  # qword
            ip_reg = "rip"
        elif arch == "x86":
            regs = prefs.X32_REGS
            for i, reg in enumerate(regs):
                reg_indexes[reg] = i
            pointer_size = 4  # dword
            ip_reg = "eip"
        else:
            print(f"Unknown CPU arch: {arch} Let's try to load it anyway.")
            ip_reg = file_info.get("ip_reg", "")
            pointer_size = file_info.get("pointer_size", 4)

        if "regs" in file_info:
            reg_indexes = {}
            for i, reg in enumerate(file_info["regs"]):
                reg_indexes[reg] = i

        trace_data.arch = arch
        trace_data.ip_reg = ip_reg
        trace_data.regs = reg_indexes
        trace_data.pointer_size = pointer_size

        reg_values = [None] * len(reg_indexes)
        trace = []
        row_id = 0
        while f.peek(1)[:1] == b"\x00":
            f.read(1)
            disasm = ""
            disasm_length = int.from_bytes(f.read(1), "little")
            if disasm_length > 0:
                disasm = f.read(disasm_length).decode()

            comment = ""
            comment_length = int.from_bytes(f.read(1), "little")
            if comment_length > 0:
                comment = f.read(comment_length).decode()

            register_changes = int.from_bytes(f.read(1), "little")
            memory_accesses = int.from_bytes(f.read(1), "little")
            flags_and_opcode_size = int.from_bytes(f.read(1), "little")  # Bitfield
            thread_id_bit = (flags_and_opcode_size >> 7) & 1  # msb
            opcode_size = flags_and_opcode_size & 15  # 4 lsb

            if thread_id_bit > 0:
                thread_id = int.from_bytes(f.read(4), "little")

            opcodes = f.read(opcode_size)

            register_change_position = []
            for _ in range(register_changes):
                register_change_position.append(int.from_bytes(f.read(1), "little"))

            register_change_new_data = []
            for _ in range(register_changes):
                register_change_new_data.append(
                    int.from_bytes(f.read(pointer_size), "little")
                )

            memory_access_flags = []
            for _ in range(memory_accesses):
                memory_access_flags.append(int.from_bytes(f.read(1), "little"))

            memory_access_addresses = []
            for _ in range(memory_accesses):
                memory_access_addresses.append(
                    int.from_bytes(f.read(pointer_size), "little")
                )

            memory_access_data = []
            for i in range(memory_accesses):
                memory_access_data.append(
                    int.from_bytes(f.read(pointer_size), "little")
                )

            reg_id = 0
            for i, change_pos in enumerate(register_change_position):
                reg_id += change_pos
                if reg_id + i < len(reg_indexes):
                    reg_values[reg_id + i] = register_change_new_data[i]

            mems = []
            mem = {}
            for i in range(memory_accesses):
                flag = memory_access_flags[i]
                value = memory_access_data[i]
                mem["access"] = "READ"
                if flag & 1 == 1:
                    mem["access"] = "WRITE"

                mem["addr"] = memory_access_addresses[i]
                mem["value"] = value
                mems.append(mem.copy())

            trace_row = {}
            trace_row["id"] = row_id
            if ip_reg:
                trace_row["ip"] = reg_values[reg_indexes[ip_reg]]
            trace_row["disasm"] = disasm
            trace_row["comment"] = comment
            trace_row["regs"] = reg_values.copy()
            trace_row["opcodes"] = opcodes.hex()
            trace_row["mem"] = mems.copy()
            trace.append(trace_row)
            row_id += 1

        trace_data.trace = trace

        while f.peek(1)[:1] == b"\x01":
            f.read(1)
            bookmark = Bookmark()
            bookmark.startrow = int.from_bytes(f.read(4), "little")
            bookmark.endrow = int.from_bytes(f.read(4), "little")
            disasm_length = int.from_bytes(f.read(1), "little")
            bookmark.disasm = f.read(disasm_length).decode()
            comment_length = int.from_bytes(f.read(1), "little")
            bookmark.comment = f.read(comment_length).decode()
            addr_length = int.from_bytes(f.read(1), "little")
            bookmark.addr = f.read(addr_length).decode()
            trace_data.add_bookmark(bookmark)

        return trace_data


def open_json_trace(filename):
    """Opens JSON trace file and reads trace data and bookmarks

    Args:
        filename: name of trace file
    """
    try:
        f = open(filename)
    except IOError:
        print("Error, could not open file.")
    else:
        with f:
            try:
                trace_data = TraceData()
                data = json.load(f)
                trace_data.bookmarks = []
                trace_data.filename = filename
                trace_data.trace = data["trace"]
                trace_data.arch = data.get("arch", "")
                trace_data.ip_reg = data.get("ip_reg", "")
                trace_data.pointer_size = data.get("pointer_size", 4)
                trace_data.regs = data.get("regs", {})
                if "bookmarks" in data:
                    for bookmark in data["bookmarks"]:
                        trace_data.add_bookmark(Bookmark(**bookmark))
                return trace_data
            except KeyError:
                print("Error while reading trace file.")
            except Exception as exc:
                print("Error while reading trace file: " + str(exc))
                print(traceback.format_exc())
    return None


def save_as_json(trace_data, filename):
    """Saves trace data to file in JSON format

    Args:
        trace_data: TraceData object
        filename: name of trace file
    """
    data = {
        "arch": trace_data.arch,
        "regs": trace_data.regs,
        "ip_reg": trace_data.ip_reg,
        "pointer_size": trace_data.pointer_size,
        "trace": trace_data.trace,
        "bookmarks": [vars(h) for h in trace_data.bookmarks],
    }
    with open(filename, "w") as f:
        json.dump(data, f)


def save_as_tv_trace(trace_data, filename):
    """Saves trace data in a default Trace Viewer format

    Args:
        trace_data: TraceData object
        filename: name of trace file
    """
    try:
        f = open(filename, "wb")
    except IOError:
        print("Error, could not write to file.")
    else:
        with f:
            trace = trace_data.trace
            f.write(b"TVTR")
            file_info = {"arch": trace_data.arch, "version": "1.0"}
            if trace_data.pointer_size:
                pointer_size = trace_data.pointer_size
            elif trace_data.arch == "x64":
                pointer_size = 8
            else:
                pointer_size = 4

            file_info["pointer_size"] = pointer_size
            file_info["regs"] = list(trace_data.regs.keys())
            file_info["ip_reg"] = trace_data.ip_reg

            json_blob = json.dumps(file_info)
            json_blob_length = len(json_blob)
            f.write((json_blob_length).to_bytes(4, byteorder="little"))
            f.write(json_blob.encode())

            for i, t in enumerate(trace):
                f.write(b"\x00")

                disasm = t["disasm"][:255]  # limit length to 0xff
                f.write((len(disasm)).to_bytes(1, byteorder="little"))
                f.write(disasm.encode())

                comment = t["comment"][:255]
                f.write((len(comment)).to_bytes(1, byteorder="little"))
                f.write(comment.encode())

                reg_change_newdata = []
                reg_change_positions = []
                pos = 0
                for reg_index, reg_value in enumerate(t["regs"]):
                    if i == 0 or reg_value != trace[i - 1]["regs"][reg_index]:
                        reg_change_newdata.append(reg_value)  # value changed
                        reg_change_positions.append(pos)
                        pos = -1
                    pos += 1

                reg_changes = len(reg_change_positions) & 0xFF
                f.write((reg_changes).to_bytes(1, byteorder="little"))

                memory_accesses = len(t["mem"]) & 0xFF
                f.write((memory_accesses).to_bytes(1, byteorder="little"))

                flag = 0
                opcodes = bytes.fromhex(t["opcodes"])
                opcode_size = len(opcodes)
                if "thread" in t:
                    flag = flag | (1 << 7)
                flags_and_opcode_size = flag | opcode_size

                f.write((flags_and_opcode_size).to_bytes(1, byteorder="little"))
                if "thread" in t:
                    f.write((t["thread"]).to_bytes(4, byteorder="little"))
                f.write(opcodes)

                for pos in reg_change_positions:
                    f.write((pos).to_bytes(1, byteorder="little"))

                for newdata in reg_change_newdata:
                    f.write((newdata).to_bytes(pointer_size, byteorder="little"))

                mem_access_flags = []
                mem_access_addresses = []
                mem_access_data = []
                for mem_access in t["mem"]:
                    flag = 0
                    if mem_access["access"].lower() == "write":
                        flag = 1
                    mem_access_flags.append(flag)
                    mem_access_data.append(mem_access["value"])
                    mem_access_addresses.append(mem_access["addr"])

                for flag in mem_access_flags:
                    f.write((flag).to_bytes(1, byteorder="little"))
                for addr in mem_access_addresses:
                    f.write((addr).to_bytes(pointer_size, byteorder="little"))
                for data in mem_access_data:
                    f.write((data).to_bytes(pointer_size, byteorder="little"))

            for bookmark in trace_data.bookmarks:
                f.write(b"\x01")
                f.write((bookmark.startrow).to_bytes(4, byteorder="little"))
                f.write((bookmark.endrow).to_bytes(4, byteorder="little"))
                disasm = bookmark.disasm[:255]
                disasm_length = len(disasm)
                f.write((disasm_length).to_bytes(1, byteorder="little"))
                f.write(disasm.encode())
                comment = bookmark.comment[:255]
                comment_length = len(comment)
                f.write((comment_length).to_bytes(1, byteorder="little"))
                f.write(comment.encode())
                addr = bookmark.addr[:255]
                addr_length = len(addr)
                f.write((addr_length).to_bytes(1, byteorder="little"))
                f.write(addr.encode())


def open_x64dbg_trace(filename):
    """Opens x64dbg trace file

    Args:
        filename: name of trace file
    Returns:
        TraceData object
    """
    with open(filename, "rb") as f:
        trace_data = TraceData()
        trace_data.filename = filename

        # check first 4 bytes
        magic = f.read(4)
        if magic != b"TRAC":
            raise ValueError("Error, wrong file format.")

        json_length_bytes = f.read(4)
        json_length = int.from_bytes(json_length_bytes, "little")

        # read JSON blob
        json_blob = f.read(json_length)
        json_str = str(json_blob, "utf-8")
        arch = json.loads(json_str)["arch"]

        reg_indexes = {}
        if arch == "x64":
            regs = prefs.X64_REGS
            ip_reg = "rip"
            capstone_mode = CS_MODE_64
            pointer_size = 8  # qword
        else:
            regs = prefs.X32_REGS
            ip_reg = "eip"
            capstone_mode = CS_MODE_32
            pointer_size = 4  # dword

        for i, reg in enumerate(regs):
            reg_indexes[reg] = i

        trace_data.arch = arch
        trace_data.ip_reg = ip_reg
        trace_data.regs = reg_indexes
        trace_data.pointer_size = pointer_size

        md = Cs(CS_ARCH_X86, capstone_mode)
        reg_values = [None] * len(reg_indexes)
        trace = []
        row_id = 0
        while f.read(1) == b"\x00":
            register_changes = int.from_bytes(f.read(1), "little")
            memory_accesses = int.from_bytes(f.read(1), "little")
            flags_and_opcode_size = int.from_bytes(f.read(1), "little")  # Bitfield
            thread_id_bit = (flags_and_opcode_size >> 7) & 1  # msb
            opcode_size = flags_and_opcode_size & 15  # 4 lsbs

            if thread_id_bit > 0:
                thread_id = int.from_bytes(f.read(4), "little")

            opcodes = f.read(opcode_size)

            register_change_position = []
            for _ in range(register_changes):
                register_change_position.append(int.from_bytes(f.read(1), "little"))

            register_change_new_data = []
            for _ in range(register_changes):
                register_change_new_data.append(
                    int.from_bytes(f.read(pointer_size), "little")
                )

            memory_access_flags = []
            for _ in range(memory_accesses):
                memory_access_flags.append(int.from_bytes(f.read(1), "little"))

            memory_access_addresses = []
            for _ in range(memory_accesses):
                memory_access_addresses.append(
                    int.from_bytes(f.read(pointer_size), "little")
                )

            memory_access_old_data = []
            for _ in range(memory_accesses):
                memory_access_old_data.append(
                    int.from_bytes(f.read(pointer_size), "little")
                )

            memory_access_new_data = []
            for i in range(memory_accesses):
                if memory_access_flags[i] & 1 == 0:
                    memory_access_new_data.append(
                        int.from_bytes(f.read(pointer_size), "little")
                    )

            reg_id = 0
            for i, change in enumerate(register_change_position):
                reg_id += change
                if reg_id + i < len(reg_indexes):
                    reg_values[reg_id + i] = register_change_new_data[i]

            # disassemble
            ip_value = reg_values[reg_indexes[ip_reg]]
            for (_address, _size, mnemonic, op_str) in md.disasm_lite(
                    opcodes, ip_value
            ):
                disasm = mnemonic
                if op_str:
                    disasm += " " + op_str

            mems = []
            mem = {}
            new_data_counter = 0
            for i in range(memory_accesses):
                flag = memory_access_flags[i]
                value = memory_access_old_data[i]
                mem["access"] = "READ"
                if flag & 1 == 0:
                    value = memory_access_new_data[new_data_counter]
                    mem["access"] = "WRITE"
                    new_data_counter += 1
                else:
                    pass
                    # memory value didn't change
                    # (it is read or overwritten with identical value)
                    # this has to be fixed somehow in x64dbg

                mem["addr"] = memory_access_addresses[i]

                # fix value (x64dbg saves all values as qwords)
                if "qword" in disasm:
                    pass
                elif "dword" in disasm:
                    value &= 0xFFFFFFFF
                elif "word" in disasm:
                    value &= 0xFFFF
                elif "byte" in disasm:
                    value &= 0xFF
                mem["value"] = value
                mems.append(mem.copy())

            trace_row = {}
            trace_row["id"] = row_id
            trace_row["ip"] = ip_value
            trace_row["disasm"] = disasm
            trace_row["regs"] = reg_values.copy()
            trace_row["opcodes"] = opcodes.hex()
            trace_row["mem"] = mems.copy()
            trace_row["comment"] = ""
            trace.append(trace_row)
            row_id += 1

        trace_data.trace = trace
        return trace_data
