import struct
import re

def extract_site_coords(file_path, max_count=None):
    count = 0
    with open(file_path, 'rb') as f:
        while True:
            header = f.read(4)
            if len(header) < 4:
                break

            rec_len, rec_typ, rec_sub = struct.unpack('<HBB', header)
            data = f.read(rec_len)

            if rec_typ == 0x32 and rec_sub == 0x1E:
                try:
                    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
                    if re.match(r'.X:\d+ Y:\d+ Site:\d+', ascii_str):
                        count += 1
                        print(f"[{count}] {ascii_str}")
                        if max_count and count >= max_count:
                            break
                except Exception as e:
                    continue

if __name__ == "__main__":
    stdf_file = "your_file.std"  # 替换为你的文件路径
    extract_site_coords(stdf_file, max_count=2000)
