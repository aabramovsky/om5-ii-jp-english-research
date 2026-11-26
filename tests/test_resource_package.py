# SPDX-License-Identifier: Apache-2.0
import json
import os
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from resource_package import extract_resource_package
from resource_candidate import make_candidate
from offline_firmware import sha256


class ResourcePackageTests(unittest.TestCase):
    def test_unknown_variant_refused(self):
        with self.assertRaisesRegex(ValueError, 'unknown variant'):
            extract_resource_package(b'', 'main')

    def test_unpinned_inputs_refused(self):
        for variant in ('stock', 'candidate'):
            for data in (b'', b'OE' + bytes(62), bytes(512)):
                with self.subTest(variant=variant, size=len(data)):
                    with self.assertRaisesRegex(ValueError, 'exact model/build/hash'):
                        extract_resource_package(data, variant)


@unittest.skipUnless(os.environ.get('OM5_TEST_STOCK'), 'Set OM5_TEST_STOCK to the exact external input')
class ResourcePackageIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = Path(os.environ['OM5_TEST_STOCK']).read_bytes()
        tr = json.loads((ROOT / 'data/english_gap_translations.json').read_text(encoding='utf-8'))
        cls.candidate = make_candidate(cls.stock, {int(k): v for k, v in tr['translations'].items()})[0]

    def test_exact_slices_and_no_other_components(self):
        hashes = {'stock': 'ff68b7bf98b1f7ff90a69b0d46c1c3e2c68673021bbc94f93c7b39b196fdd2cf',
                  'candidate': '82aebb31264c29ce64921f8cecdc8a431a780df6d281d14b5706a2f85dc602fc'}
        for variant in hashes:
            full = getattr(self, variant)
            package = extract_resource_package(full, variant)
            self.assertEqual(package, full[24903680:37486592])
            self.assertEqual(len(package), 12582912)
            self.assertEqual(sha256(package), hashes[variant])
            self.assertEqual(struct.unpack_from('<H', package, 20)[0], 0x101)
            with self.assertRaisesRegex(ValueError, 'exact model/build/hash'):
                extract_resource_package(package, variant)
            with self.assertRaisesRegex(ValueError, 'exact model/build/hash'):
                extract_resource_package(full, 'stock' if variant == 'candidate' else 'candidate')

    def test_full_length_wrong_model_and_build_refused(self):
        for at in (2, 16):
            bad = bytearray(self.stock)
            bad[at] ^= 1
            with self.assertRaisesRegex(ValueError, 'exact model/build/hash'):
                extract_resource_package(bad, 'stock')
