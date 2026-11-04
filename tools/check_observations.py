#!/usr/bin/env python3
"""Validate real observation input without modifying it or synthesizing values."""
import argparse
import csv
import datetime as dt
import math
from pathlib import Path

FIELDS = ['FREQ', 'TIME_PERIOD', 'SERIES_CODE', 'OBS_VALUE', 'SeriesName', 'Legend']


def validate(path):
    seen = set()
    frequencies = {}
    errors = []
    count = 0
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            return 0, ['Header must be exactly: ' + ','.join(FIELDS)]
        for n, row in enumerate(reader, 2):
            count += 1
            if None in row or any(v is None for v in row.values()):
                errors.append(f'Line {n}: expected exactly six CSV fields.')
                continue
            date = row['TIME_PERIOD']
            code = row['SERIES_CODE']
            freq = row['FREQ']
            try:
                parsed = dt.date.fromisoformat(date)
                if parsed.isoformat() != date: raise ValueError()
            except ValueError:
                errors.append(f'Line {n}: TIME_PERIOD must be ISO YYYY-MM-DD.')
                parsed = None
            if not code or code != code.strip() or ',' in code or '<X>' in code:
                errors.append(f'Line {n}: one nonblank trimmed concrete SERIES_CODE is required.')
            if freq not in {'M','Q','W','D','A'}:
                errors.append(f'Line {n}: invalid FREQ.')
            previous_freq = frequencies.setdefault(code, freq)
            if previous_freq != freq:
                errors.append(f'Line {n}: a series cannot mix frequencies.')
            if parsed and freq in {'M','Q','A'} and parsed.day != 1:
                errors.append(f'Line {n}: monthly, quarterly, and annual periods use their first day.')
            if parsed and freq == 'Q' and parsed.month not in {1,4,7,10}:
                errors.append(f'Line {n}: quarterly dates must be quarter starts.')
            if parsed and freq == 'A' and parsed.month != 1:
                errors.append(f'Line {n}: annual dates must be year starts.')
            if row['OBS_VALUE']:
                try:
                    if not math.isfinite(float(row['OBS_VALUE'])): raise ValueError()
                except ValueError:
                    errors.append(f'Line {n}: OBS_VALUE must be a finite decimal or empty for missing data.')
            key = (code,date)
            if key in seen: errors.append(f'Line {n}: duplicate SERIES_CODE/TIME_PERIOD.')
            seen.add(key)
    return count, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', default=Path(__file__).resolve().parents[1]/'data'/'observations.csv')
    args = parser.parse_args()
    count, errors = validate(args.path)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print(f'Input valid: {count} observations.' + (' No dated values have been supplied.' if not count else ''))


if __name__ == '__main__': main()
