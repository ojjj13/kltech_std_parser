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
    try:
        # ✅ 真实 TestNumber 是前4字节
        test_num = struct.unpack('<I', data[0:4])[0]

        head_num = data[4]
        site_num = data[5]
        test_flg = data[6]
        # parm_flg = data[7]  # 可忽略

        # ✅ 结果值在偏移 8
        result = struct.unpack('<f', data[8:12])[0]
        pos = 12

        # 解析 TestName, Alarm_ID, Units
        test_txt, pos = read_stdf_cn_string(data, pos)
        _, pos = read_stdf_cn_string(data, pos)      # ALARM_ID
        units, pos = read_stdf_cn_string(data, pos)  # UNITS

        # 跳过 4 字节 padding
        if pos + 4 <= len(data):
            pos += 4

        # 读取上下限
        lo_limit = hi_limit = None
        if pos + 4 <= len(data):
            lo_limit = struct.unpack('<f', data[pos:pos+4])[0]
            pos += 4
        if pos + 4 <= len(data):
            hi_limit = struct.unpack('<f', data[pos:pos+4])[0]
            pos += 4

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
