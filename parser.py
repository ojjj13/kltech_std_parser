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
    """Parse a single PTR record from binary bytes."""
    record = {}
    try:
        pos = 0
        if len(data) < 12:
            return {'Error': 'Record too short'}

        record['TestNumber'] = struct.unpack('<I', data[pos:pos + 4])[0]
        pos += 4

        head_num = data[pos]
        pos += 1
        record['Site'] = data[pos]
        pos += 1
        record['TestFlag'] = data[pos]
        pos += 1
        parm_flg = data[pos]
        pos += 1
        record['Result'] = struct.unpack('<f', data[pos:pos + 4])[0]
        pos += 4

        record['TestName'], pos = read_stdf_cn_string(data, pos)
        _, pos = read_stdf_cn_string(data, pos)  # Alarm ID

        if pos >= len(data):
            return record

        # Optional fields
        opt_flag = data[pos]
        pos += 1
        pos += 3  # res_scal, llm_scal, hlm_scal

        if pos + 8 > len(data):
            return record

        record['LoLimit'] = struct.unpack('<f', data[pos:pos + 4])[0]
        pos += 4
        record['HiLimit'] = struct.unpack('<f', data[pos:pos + 4])[0]
        pos += 4

        record['Units'], pos = read_stdf_cn_string(data, pos)

        # skip remaining Cn fields if present
        for _ in range(3):
            _, pos = read_stdf_cn_string(data, pos)

        if pos + 8 <= len(data):
            record['LoSpec'] = struct.unpack('<f', data[pos:pos + 4])[0]
            pos += 4
            record['HiSpec'] = struct.unpack('<f', data[pos:pos + 4])[0]
            pos += 4

        return record

    except Exception as e:
        record['Error'] = str(e)
        return record


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
