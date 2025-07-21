import csv
from collections import defaultdict, OrderedDict
import sys
import builtins


def reformat_csv(input_csv, output_csv):
    # Maps test name -> {'LoLimit': value, 'HiLimit': value, 'Units': value}
    test_meta = {}
    # Keep order of tests as first encountered
    test_order = []

    # Temporary storage for chip data per site
    current_rows = defaultdict(lambda: OrderedDict())
    rows_by_site = defaultdict(list)

    with builtins.open(input_csv, newline='') as f:
        reader = csv.DictReader(f)
        for record in reader:
            site = record.get('Site')
            testname = record.get('TestName')
            result = record.get('Result')

            # store meta info once
            if testname not in test_meta:
                test_meta[testname] = {
                    'LoLimit': record.get('LoLimit', ''),
                    'HiLimit': record.get('HiLimit', ''),
                    'Units': record.get('Units', ''),
                }
                test_order.append(testname)

            row = current_rows[site]
            if testname in row:
                # start a new chip row for this site
                rows_by_site[site].append(row)
                row = OrderedDict()
                current_rows[site] = row
            row[testname] = result

    # append remaining rows
    for site, row in current_rows.items():
        if row:
            rows_by_site[site].append(row)

    # Build final output rows
    header_tests = ['Site'] + test_order
    header_units = ['Unit'] + [test_meta[t]['Units'] for t in test_order]
    header_hi = ['HiLimit'] + [test_meta[t]['HiLimit'] for t in test_order]
    header_lo = ['LoLimit'] + [test_meta[t]['LoLimit'] for t in test_order]

    output_rows = [header_tests, header_units, header_hi, header_lo]

    # Combine rows from all sites sequentially
    for site in sorted(rows_by_site.keys()):
        for row in rows_by_site[site]:
            result_row = [site] + [row.get(t, '') for t in test_order]
            output_rows.append(result_row)

    with builtins.open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output_rows)


if __name__ == '__main__':
    input_csv = './ptr_results.csv'
    output_csv = './final_results.csv'
    reformat_csv(input_csv, output_csv)
