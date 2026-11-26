# SPDX-License-Identifier: Apache-2.0
import unittest
import sys
import struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from resource_candidate import encode_payload, make_candidate, make_strings
from offline_firmware import parse_strings


def fixture(japanese=False, text='日本語'):
    data = bytearray(b'\0'*8 + b'\0\0')
    pointers = [0xa407f548] * 4909
    for sid, text in ({23:text} if japanese else {14:'English'}).items():
        pointers[sid] = 0xa407f540 + len(data)
        data.extend(text.encode('utf-16-le') + b'\0\0')
    data.extend(bytes((-len(data)) % 4))
    start = len(data)
    data.extend(struct.pack('<4909I', *pointers))
    end = len(data)
    tail = bytearray(148)
    name = ('OlympusLanguage_jpntft' if japanese else 'OlympusLanguage_enutft').encode('utf-16-le')
    tail[74:74+len(name)] = name
    tail[140:143] = b'\x32\x01\x01'
    data.extend(tail)
    struct.pack_into('<II', data, 0, 0xa407f540+start, 0xa407f540+end)
    return bytes(data)


class CandidateTests(unittest.TestCase):
    def test_encode_known_vector(self):
        self.assertEqual(encode_payload(bytes(range(16))), bytes([253,255,252,254,250,248,251,249,244,245,246,247,241,243,242,240]))

    def test_unaligned_encode_refused(self):
        with self.assertRaisesRegex(ValueError, 'unaligned'):
            encode_payload(bytes(17))

    def test_nonstock_candidate_refused(self):
        for data in (b'', b'OE'+bytes(62), bytes(1024)):
            with self.assertRaisesRegex(ValueError, 'pinned'):
                make_candidate(data, {})

    def test_bad_string_input_refused(self):
        with self.assertRaisesRegex(ValueError, 'truncated'):
            make_strings(b'', b'', {})

    def test_stock_text_and_jp_font_descriptor_preserved(self):
        en, jp = fixture(), fixture(True)
        out, expected = make_strings(en, jp, {23:'English'})
        result = parse_strings(out)
        self.assertEqual(result['strings'], expected)
        self.assertEqual(result['strings'][14], 'English')
        self.assertEqual(result['strings'][23], 'English')
        self.assertEqual(result['strings'][4908], '')
        self.assertEqual(out[result['table_end']:result['table_end']+148], jp[-148:])
        self.assertEqual(len(out) % 512, 0)

    def test_missing_or_extra_translation_refused(self):
        for tr in ({}, {23:'English', 24:'bad'}):
            with self.assertRaisesRegex(ValueError, 'exactly cover'):
                make_strings(fixture(), fixture(True), tr)

    def test_invalid_text_refused(self):
        for value in ('', '\0', 'English\x01', '日本語', 9):
            with self.assertRaises(ValueError):
                make_strings(fixture(), fixture(True), {23:value})

    def test_capacity_overflow_refused(self):
        with self.assertRaisesRegex(ValueError, 'capacity'):
            make_strings(fixture(), fixture(True), {23:'English'}, limit=2048)

    def test_unknown_font_tail_refused(self):
        with self.assertRaisesRegex(ValueError, 'metadata tail'):
            make_strings(fixture(), fixture(True)+b'\1', {23:'English'})

    def test_special_token_removal_or_insertion_refused(self):
        for source, translated in [('@A032@日本語','English'), ('日本語','@A032@English'),
                                   ('$日本語','English'), ('日本語','$English')]:
            with self.assertRaisesRegex(ValueError, 'special tokens'):
                make_strings(fixture(), fixture(True, source), {23:translated})

    def test_special_tokens_preserved(self):
        _, expected = make_strings(fixture(), fixture(True, '@A032@$日本語'), {23:'@A032@$English'})
        self.assertEqual(expected[23], '@A032@$English')

    def test_incomplete_or_stray_escape_refused(self):
        for text in ('English @A032', 'English A032@', 'English @ZZZZ@', 'English @@',
                     'English @A032@ @A06B'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'malformed special tokens'):
                make_strings(fixture(), fixture(True), {23:text})

    def test_control_order_and_leading_dollar_preserved(self):
        cases = [('@A032@日本語@A06B@', '@A06B@English@A032@'),
                 ('@A032@$日本語', '$@A032@English'),
                 ('$日本語', 'English$'),
                 ('$日本語@A032@', 'English$@A032@')]
        for source, translated in cases:
            with self.subTest(source=source, translated=translated), self.assertRaisesRegex(ValueError, 'changed special tokens'):
                make_strings(fixture(), fixture(True, source), {23:translated})


if __name__ == '__main__':
    unittest.main()
