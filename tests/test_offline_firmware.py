# SPDX-License-Identifier: Apache-2.0
"""Synthetic fixtures only; never reads a camera or executes firmware."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import offline_firmware as fw


def fixture(payload=bytes(16), model=b'\x14\x80', kind=0x101):
    head = bytearray(32)
    head[:4] = b'OE' + model
    struct.pack_into('<IIHHH', head, 8, 0x42140000, len(payload), 0x1100, 0, kind)
    trailer = bytearray(head)
    struct.pack_into('<I', trailer, 28, -(fw.sum32(head)*2 + fw.sum32(payload)) & 0xffffffff)
    # Fixture encoder deliberately straightforward, independent of vectorized decoder.
    stored = bytearray(len(payload))
    for base in range(0, len(payload), 16):
        for i, j in enumerate(fw.PERM):
            stored[base+j] = payload[base+i] ^ 255
    return bytes(head+stored+trailer)


class ContainerTests(unittest.TestCase):
    def test_valid_component_decode_and_digest(self):
        payload = bytes(range(32))
        result = fw.parse_container(fixture(payload))
        self.assertEqual(result[0]['payload'], payload)
        self.assertEqual(result[0]['kind'], 0x101)
        self.assertTrue(result[0]['checksum_valid'])

    def test_reject_every_truncation(self):
        data = fixture()
        for n in range(len(data)):
            with self.subTest(length=n), self.assertRaises(ValueError):
                fw.parse_container(data[:n])

    def test_wrong_model(self):
        with self.assertRaisesRegex(ValueError, 'wrong model'):
            fw.parse_container(fixture(model=b'\x14\x40'))

    def test_checksum_corruption(self):
        data = bytearray(fixture())
        data[32] ^= 1
        with self.assertRaisesRegex(ValueError, 'checksum'):
            fw.parse_container(data)

    def test_bad_header_trailer_and_unbounded_length(self):
        for at, value in [(0, 0), (28, 1), (12, 255)]:
            data = bytearray(fixture())
            data[at] = value
            with self.assertRaises(ValueError):
                fw.parse_container(data)

    def test_duplicate_type_and_trailing_junk(self):
        for data in (fixture()+fixture(), fixture()+b'junk'):
            with self.assertRaises(ValueError):
                fw.parse_container(data)

    def test_stock_identity_gate(self):
        with self.assertRaisesRegex(ValueError, 'pinned'):
            fw.verify_stock(fixture())
        with self.assertRaisesRegex(ValueError, 'pinned'):
            fw.verify_stock(bytes(fw.STOCK_SIZE))


class Lz4Tests(unittest.TestCase):
    def test_literal(self):
        self.assertEqual(fw.decompress_lz4(b'\x50hello', 5), b'hello')

    def test_overlapping_match(self):
        self.assertEqual(fw.decompress_lz4(b'\x15a\x01\x00', 10), b'a'*10)

    def test_reject_malformed(self):
        for data, size in [(b'\xf0\xff', 300), (b'\x50hi', 5), (b'\x00\x00\x00', 4),
                           (b'\x00\x01\x00', 4), (b'\x10a\x01', 5), (b'\x15a\x01\x00', 9),
                           (b'\x50hello', 6), (b'\x50hello', 4), (b'', 0), (b'', 2**32)]:
            with self.subTest(data=data, size=size), self.assertRaises(ValueError):
                fw.decompress_lz4(data, size)


class ResourceTests(unittest.TestCase):
    def test_directory_and_out_of_bounds(self):
        data = struct.pack('<4I', 0x1000+16, 16, 0, 0)+bytes(16)
        self.assertEqual(fw.parse_resource_directory(data, 0x1000)[0]['decoded'], bytes(16))
        with self.assertRaises(ValueError):
            fw.parse_resource_directory(data[:-1], 0x1000)

    def test_overlap_and_flags(self):
        for data in (struct.pack('<4I', 0x1020, 16, 0, 0)*2+bytes(16),
                     struct.pack('<4I', 0x1010, 16, 1, 0)+bytes(16)):
            with self.assertRaises(ValueError):
                fw.parse_resource_directory(data, 0x1000)

    def test_strings_precede_pointer_table(self):
        data = struct.pack('<II', 0x1010, 0x1018)+'A\0B\0'.encode('utf-16-le')+struct.pack('<II', 0x1008, 0x100c)
        self.assertEqual(fw.parse_strings(data, 0x1000, 2)['strings'], ['A', 'B'])
        for pointer in (0x1000, 0x1010, 0xffffffff, 0x1009):
            changed = data[:16]+struct.pack('<I', pointer)+data[20:]
            with self.assertRaises(ValueError):
                fw.parse_strings(changed, 0x1000, 2)

    def test_string_termination_and_count(self):
        data = struct.pack('<II', 0x100c, 0x1010)+b'A\0B\0'+struct.pack('<I', 0x1008)
        with self.assertRaisesRegex(ValueError, 'unterminated'):
            fw.parse_strings(data, 0x1000, 1)
        with self.assertRaisesRegex(ValueError, 'count'):
            fw.parse_strings(data, 0x1000, 2)

    def test_unaligned_pointer_table(self):
        data = struct.pack('<II', 0x100f, 0x1013)+b'A\0\0\0xxx'+struct.pack('<I', 0x1008)
        with self.assertRaisesRegex(ValueError, 'bounds'):
            fw.parse_strings(data, 0x1000, 1)


if __name__ == '__main__':
    unittest.main()
