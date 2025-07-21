import struct


def read_stdf_cn_string(data, pos):
    """Read STDF Cn (ASCII) string starting at *pos*.

    Returns the decoded string and the new position after the field.
    """
    if pos >= len(data):
        return "", pos
    length = data[pos]
    pos += 1
    raw = data[pos:pos + length]
    pos += length
    try:
        return raw.decode("ascii", "ignore"), pos
    except Exception:
        return "", pos


def parse_ptr_record(data):
    try:
        if len(data) < 12:
            return {'Error': 'Record too short'}

        test_num = struct.unpack('<I', data[0:4])[0]
        site_num = data[5]
        test_flg = data[6]
        result = struct.unpack('<f', data[8:12])[0]

        # ----- Step 1: 解 TestName -----
        pos = 12
        test_txt, pos = read_stdf_cn_string(data, pos)

        # 尝试读取 alarm ID（通常是 Cn 类型，可能为 0）
        _, pos = read_stdf_cn_string(data, pos)

        # ----- Step 2: 结尾结构判断 -----
        units = ''
        lo_limit = None
        hi_limit = None

        # Step 2.1: 从末尾尝试解析 8 字节为 float：Hi/Lo Limit
        if len(data) >= 8:
            try:
                hi_limit = struct.unpack('<f', data[-4:])[0]
                lo_limit = struct.unpack('<f', data[-8:-4])[0]
            except:
                pass

        # Step 2.2: 倒数第12字节可能是 Units 长度（如：02 6D 56）
        if len(data) >= 12:
            units_len = data[-12]
            if 1 <= units_len <= 8 and len(data) >= (11 + units_len):
                raw = data[-11:-11+units_len]
                try:
                    units = raw.decode('ascii', errors='ignore')
                except:
                    units = ''

        return {
            'Site': site_num,
            'TestNumber': test_num,
            'Result': result,
            'TestFlag': test_flg,
            'TestName': test_txt,
            'Units': units,
            'LoLimit': lo_limit,
            'HiLimit': hi_limit
        }

    except Exception as e:
        return {'Error': str(e)}


def parse_hex_file_to_csv(hex_file, csv_file):
    """Parse hex strings from *hex_file* and write records to *csv_file*."""
    import csv

    records = []
    with open(hex_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = bytes.fromhex(line)
            except ValueError:
                continue
            rec = parse_ptr_record(data)
            records.append(rec)

    if not records:
        return

    fieldnames = list(records[0].keys())
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    parse_hex_file_to_csv("hex_code.txt", "result.csv")
