import csv
from collections import defaultdict
from typing import List

from extract_site_coords import extract_site_coords


def merge_with_site_coords(final_csv: str, stdf_file: str, output_csv: str) -> None:
    """Merge ``final_csv`` with site coordinates extracted from ``stdf_file``.

    The order of the output rows follows the order of coordinates in the STDF
    file so that the final CSV reflects test execution order.
    """

    coords = extract_site_coords(stdf_file, verbose=False)

    # read existing final_results
    with open(final_csv, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) < 5:
        raise ValueError("final_results.csv does not appear to have the expected format")

    header_tests = rows[0] + ["X", "Y"]
    header_units = rows[1] + ["", ""]
    header_hi = rows[2] + ["", ""]
    header_lo = rows[3] + ["", ""]

    data_rows = rows[4:]

    site_pool: defaultdict[str, List[List[str]]] = defaultdict(list)
    for r in data_rows:
        if r:
            site_pool[r[0]].append(r)

    ordered_rows: List[List[str]] = []
    for c in coords:
        site = str(c["Site"])
        if site_pool[site]:
            row = site_pool[site].pop(0)
            row += [str(c["X"]), str(c["Y"])]
            ordered_rows.append(row)

    # append any remaining rows that had no matching coordinate
    for remain_rows in site_pool.values():
        for r in remain_rows:
            r += ["", ""]
            ordered_rows.append(r)

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header_tests)
        writer.writerow(header_units)
        writer.writerow(header_hi)
        writer.writerow(header_lo)
        writer.writerows(ordered_rows)


if __name__ == "__main__":
    merge_with_site_coords("final_results.csv", "your_file.std", "final_with_coords.csv")
