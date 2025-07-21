import struct
import csv
import re

def read_stdf_cn_string(data, pos):
    if pos >= len(data):
        return '', pos
    length = data[pos]
    pos += 1
    if pos + length > len(data):
        return '', pos + length
    string = data[pos:pos+length].decode('ascii', errors='ignore')
    pos += length
    return string, pos

def extract_test_number_from_name(name):
    m = re.search(r'-(\d+)$', name)
    return int(m.group(1)) if m else None

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

        # Optional fields (OPT_FLAG, scaling factors)
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

def read_stdf_file(file_path):
    ptr_records = []
    with open(file_path, 'rb') as f:
        count = 0
        while True:
            header = f.read(4)
            if len(header) < 4:
                break
            rec_len, rec_type, rec_sub = struct.unpack('<HBB', header)
            data = f.read(rec_len)

            if rec_type == 15 and rec_sub == 10:  # PTR
                if count < 5:
                    print(f"\n📦 Raw PTR Record {count+1} ({rec_len} bytes):")
                    print("HEX:", data.hex(" "))
                    print("ASCII:", ''.join([chr(b) if 32 <= b <= 126 else '.' for b in data]))
                    count += 1

                parsed = parse_ptr_record(data)
                if 'Error' not in parsed:
                    ptr_records.append(parsed)

    return ptr_records

def write_csv(ptr_records, output_csv):
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'Site', 'TestNumber', 'Result', 'TestFlag',
            'TestName', 'Units', 'LoLimit', 'HiLimit'
        ])
        writer.writeheader()
        writer.writerows(ptr_records)

if __name__ == "__main__":
    input_file = "BYD836B_sample.std"
    output_file = "ptr_results.csv"

    print(f"\n📥 Reading: {input_file}")
    ptr_data = read_stdf_file(input_file)

    print(f"\n🖨️ Preview of first 5 parsed PTR records:\n" + "-"*60)
    for record in ptr_data[:5]:
        print(record)
    print("-"*60 + f"\n📊 Total PTR records parsed: {len(ptr_data)}")

    write_csv(ptr_data, output_file)
    print(f"\n✅ CSV exported to: {output_file}")
