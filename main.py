REGFLAG_END_OF_TABLE = 0xFD
REGFLAG_DELAY = 0xFE

# reg, count, cmd
struct_sizes = [1, 1, 64]

def main():
    hex_arr = []
    hex_raw_arr = []
    count = 0
    need_cnt = False
    need_delay_amt = False
    delay_amt = 0
    def inner_seq():
        return len(cur_outer_tbl())-1
    def cur_outer_tbl():
        return hex_arr[len(hex_arr)-1][1]
    def cur_tbl():
        return cur_outer_tbl()[inner_seq()]
    def append_sof():
        hex_arr.append(["start_of_table", []])
    with open("hexes.txt", "r") as hexes_hdl:
        append_sof()
        for line in hexes_hdl:
            hexes = line.split()
            name = hexes[0]
            hex_arr[len(hex_arr)-1][0] = name
            hexes = hexes[1:]
            for _hex in hexes:
                if _hex == ' ':
                    continue
                if _hex == '00': # only cond to pass is if in cmd mode
                    if count <= 0:
                        continue
                _hex = int(_hex, 16)
                hex_raw_arr.append(_hex)
                if need_cnt:
                    count = _hex
                    (cur_tbl())[1] = count
                    need_cnt = False
                    continue
                elif need_delay_amt:
                    print("delay_amt: ", _hex)
                    delay_amt = _hex
                    (cur_tbl())[1] = delay_amt
                    need_delay_amt = False
                    count = 0
                elif count > 0:
                    count -= 1
                    (cur_tbl())[2].append("0x"+format(_hex, '02x'))
                elif is_regflag_end_of_table(_hex):
                    (cur_outer_tbl()).append(['REGFLAG_END_OF_TABLE', "0x"+format(0, '02x'), []])
                    append_sof()
                else:
                    if is_regflag_delay(_hex):
                        print("_hex: ", _hex)
                        need_delay_amt = True
                        (cur_outer_tbl()).append(['REGFLAG_DELAY', delay_amt, []])
                        continue
                    elif count == 0:
                        need_cnt = True
                    (cur_outer_tbl()).append(["0x"+format(_hex, '02x'), 0, []])
    print(hex_arr)
    for seq in hex_arr:
        print(construct_c_array(seq))

def is_regflag_end_of_table(hex):
    return hex == REGFLAG_END_OF_TABLE

def is_regflag_delay(hex):
    return hex == REGFLAG_DELAY

def construct_c_array(hex_seq_arr):
    c_arr = ""
    c_arr += "static struct LCM_setting_table " + hex_seq_arr[0] + "[] = {\n"
    for idx, seq in enumerate(hex_seq_arr[1]):
        c_arr += "\t{" + seq[0] + ", " + str(seq[1]) + (", " if seq[2] != [] else ", {}")
        for idx, cmd in enumerate(seq[2]):
            c_arr += cmd if idx != 0 else "{" + cmd
            if idx < len(seq[2])-1:
                c_arr += ", "
            else:
                c_arr += "}"
        c_arr += "}\n" if idx == len(hex_seq_arr[1])-1 else "},\n"
    c_arr += "};\n"
    return c_arr

main()