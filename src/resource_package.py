# SPDX-License-Identifier: Apache-2.0
"""Fixed E148/1100 resource-component extraction, offline only. No device transport."""
from offline_firmware import parse_container, require, sha256, STOCK_SHA256, verify_stock

CANDIDATE_SHA256 = '68f5d1e8f7c2ed7c64a238b0f9ccfb8446ae9c78117ed632df930c7f44e16ad5'
PACKAGE_HASHES = {
    'candidate': '82aebb31264c29ce64921f8cecdc8a431a780df6d281d14b5706a2f85dc602fc',
    'stock': 'ff68b7bf98b1f7ff90a69b0d46c1c3e2c68673021bbc94f93c7b39b196fdd2cf',
}


def extract_resource_package(full, variant):
    require(variant in PACKAGE_HASHES, 'unknown variant')
    expected = STOCK_SHA256 if variant == 'stock' else CANDIDATE_SHA256
    require(sha256(full) == expected, 'wrong exact model/build/hash')
    if variant == 'stock':
        verify_stock(full)
    blocks = parse_container(full)
    require([b['kind'] for b in blocks] == [0x100, 0x101, 0x106, 0x10e, 0x102], 'wrong component layout')
    b = blocks[1]
    require((b['offset'], b['address'], b['size'], b['version_raw']) ==
            (24903680, 0x42140000, 12582848, 256), 'wrong resource header')
    # This component's own version remains 0x0100 even in the official 1.1 bundle.
    # The full bundle digest is the build gate; do not interpret this field as firmware 1.00.
    result = full[b['offset']:b['offset'] + b['size'] + 64]
    parsed = parse_container(result)
    require(len(parsed) == 1 and parsed[0]['kind'] == 0x101, 'not a resource-only package')
    require(sha256(result) == PACKAGE_HASHES[variant], 'resource package digest mismatch')
    return result
