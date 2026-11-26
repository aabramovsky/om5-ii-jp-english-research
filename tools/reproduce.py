# SPDX-License-Identifier: Apache-2.0
"""Offline reproduction; no network or device API. Default operation writes no files."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from offline_firmware import require, sha256, STOCK_SIZE
from resource_candidate import make_candidate
from resource_package import extract_resource_package, CANDIDATE_SHA256, PACKAGE_HASHES


def build(stock):
    translations = json.loads((ROOT / 'data/english_gap_translations.json').read_text(encoding='utf-8'))
    translations = {int(k): v for k, v in translations['translations'].items()}
    full, patches, strings, expected = make_candidate(stock, translations)
    require(sha256(full) == CANDIDATE_SHA256, 'full r01 digest mismatch')
    candidate = extract_resource_package(full, 'candidate')
    stock_resource = extract_resource_package(stock, 'stock')
    result = {
        'schema': 1, 'model': 'E148', 'base_firmware': '1.1',
        'stock_sha256': sha256(stock), 'full_candidate_sha256': sha256(full),
        'resource_sha256': sha256(candidate), 'stock_resource_sha256': sha256(stock_resource),
        'resource_bytes': len(candidate), 'strings_bytes': len(strings),
        'string_count': len(expected), 'research_translation_count': len(translations),
        'decoded_patch_ranges': [{'offset': o, 'length': len(a),
                                  'old_sha256': sha256(a), 'new_sha256': sha256(b)}
                                 for o, a, b in patches],
        'device_access': False, 'hardware_safety_proven': False,
    }
    artifacts = {'JP_EN_resources.research-bin': candidate,
                 'STOCK_resources.research-bin': stock_resource,
                 'build.json': (json.dumps(result, indent=2) + '\n').encode('utf-8')}
    return artifacts, result


def read_stock(path):
    # Reject special/oversized inputs before opening, then recheck the opened file.
    path = Path(path)
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and info.st_size == STOCK_SIZE,
            'stock must be an ordinary file of the exact expected size')
    with path.open('rb') as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_size == STOCK_SIZE,
                'opened stock has unexpected type or size')
        data = stream.read(STOCK_SIZE + 1)
    require(len(data) == STOCK_SIZE, 'stock size changed during bounded read')
    return data


def write_new_directory(directory, artifacts):
    directory = Path(directory)
    require(not directory.exists(), 'output directory already exists; refusing overwrite')
    require(directory.name.upper() not in ('DCOLYMP', 'OMKIT'), 'updater/loader output directory refused')
    require(directory.parent.is_dir(), 'output parent must already exist')
    directory.mkdir(exist_ok=False)
    pending = directory / '.INCOMPLETE'
    pending.mkdir(exist_ok=False)
    try:
        for name, data in artifacts.items():
            staged = pending / (name + '.partial')
            with staged.open('xb') as stream:
                require(stream.write(data) == len(data), 'short output write')
                stream.flush()
                os.fsync(stream.fileno())
            require(staged.stat().st_size == len(data), 'output size readback mismatch')
            require(sha256(staged.read_bytes()) == sha256(data), 'output hash readback mismatch')
        # No final name is exposed until the complete set has passed disk readback.
        for name in artifacts:
            target = directory / name
            require(not target.exists(), 'unexpected existing output file')
            (pending / (name + '.partial')).rename(target)
        pending.rmdir()
    except (OSError, ValueError) as error:
        raise ValueError('incomplete output retained at ' + str(directory)
                         + '; inspect .INCOMPLETE; ' + str(error)) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stock', required=True, type=Path)
    parser.add_argument('--output-dir', type=Path,
                        help='Optional NEW local research directory; default writes no files')
    args = parser.parse_args(argv)
    try:
        if args.output_dir is not None:
            require(not args.output_dir.exists(), 'output directory already exists; refusing overwrite')
        artifacts, result = build(read_stock(args.stock))
        if args.output_dir is not None:
            write_new_directory(args.output_dir, artifacts)
        result['files_written'] = len(artifacts) if args.output_dir is not None else 0
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError) as error:
        print('Refused: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
