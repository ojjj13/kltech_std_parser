import struct
import re


def extract_site_coords(file_path, max_count=None, verbose=True):
    """Extract site coordinate strings from an STDF file.

    Parameters
    ----------
    file_path : str
        Path to the STDF file.
    max_count : int, optional
        Maximum number of records to return. ``None`` means no limit.
    verbose : bool, optional
        If ``True`` the extracted strings will be printed.

    Returns
    -------
    list[dict]
        A list of dictionaries in the order encountered.  Each dictionary
        contains ``'X'``, ``'Y'`` and ``'Site'`` keys.
    """

    coords = []
    count = 0
    pattern = re.compile(r"X:(\d+)\s+Y:(\d+)\s+Site:(\d+)")

    with open(file_path, "rb") as f:
        while True:
            header = f.read(4)
            if len(header) < 4:
                break

            rec_len, rec_typ, rec_sub = struct.unpack("<HBB", header)
            data = f.read(rec_len)

            if rec_typ == 0x32 and rec_sub == 0x1E:
                ascii_str = "".join(
                    chr(b) if 32 <= b < 127 else "." for b in data
                )
                m = pattern.search(ascii_str)
                if m:
                    entry = {"X": int(m.group(1)), "Y": int(m.group(2)), "Site": m.group(3)}
                    coords.append(entry)
                    count += 1
                    if verbose:
                        print(f"[{count}] {ascii_str}")
                    if max_count and count >= max_count:
                        break

    return coords


if __name__ == "__main__":
    stdf_file = "your_file.std"  # Replace with your actual file
    extract_site_coords(stdf_file, max_count=2000)
