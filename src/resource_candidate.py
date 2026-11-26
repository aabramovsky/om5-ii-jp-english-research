# SPDX-License-Identifier: Apache-2.0
"""Offline E148/1100 JP-slot experiment. No device, SD, network or updater code."""
import struct
import re
from offline_firmware import (PERM, parse_container, parse_resource_directory,
                              parse_strings, require, sha256, sum32, verify_stock)

ORIGIN = 0x42140020
RESERVE = 0x8871e0
STRING_LIMIT = 0x5fc00
JP_DESCRIPTOR = 10 * 16
JP_FONT_SHA = '7fc31c0938eadd3bbfe0d9120078dd6861de0cec53bfa6996dc6a9b1c64505f5'


def encode_payload(data):
    require(len(data) % 16 == 0, 'unaligned payload')
    out = bytearray(len(data))
    inverted = bytes(data).translate(bytes(range(255, -1, -1)))
    for decoded, stored in enumerate(PERM):
        out[stored::16] = inverted[decoded::16]
    return bytes(out)


def make_strings(english, japanese, translations, limit=STRING_LIMIT):
    en, jp = parse_strings(english), parse_strings(japanese)
    missing = {i for i, (a, b) in enumerate(zip(en['strings'], jp['strings'])) if b and not a}
    require(set(translations) == missing, 'translation IDs must exactly cover JP nonempty / EN empty')
    # Copy the complete English text area and pointer table; replace only the
    # 39 gap-entry pointers below. The original English resource stays unchanged.
    out = bytearray(english[:en['table_start']])
    pointers = list(struct.unpack_from('<4909I', english, en['table_start']))
    expected = list(en['strings'])
    for sid in sorted(translations):
        text = translations[sid]
        require(isinstance(text, str) and text and '\0' not in text, 'invalid translation')
        require(all(c in '\r\n' or 32 <= ord(c) <= 126 for c in text), 'translation must use tested ASCII glyphs')
        original = jp['strings'][sid]
        # Reject stray/incomplete escapes instead of treating their ASCII bytes as glyphs.
        icon_pattern = r'@[0-9A-Fa-f]{4}@'
        require('@' not in re.sub(icon_pattern, '', text), 'translation has malformed special tokens')
        # These additions retain the source controls in order; reordering needs explicit review.
        controls = icon_pattern + r'|\$'
        require(re.findall(controls, text) == re.findall(controls, original)
                and text.startswith('$') == original.startswith('$'), 'translation changed special tokens')
        pointers[sid] = en['load_base'] + len(out)
        expected[sid] = text
        out.extend(text.encode('utf-16-le') + b'\0\0')
    out.extend(bytes((-len(out)) % 4))
    start = len(out)
    out.extend(struct.pack('<4909I', *pointers))
    end = len(out)
    # The two 74-byte descriptors: font 0 empty, font 1 OlympusLanguage_jpntft.
    # Keep the exact JP descriptor and its font resource; all JP font glyphs are checked separately.
    tail = japanese[jp['table_end']:]
    require(len(tail) >= 148 and not any(tail[148:]), 'unknown JP font metadata tail')
    require(tail[:74] == bytes(74), 'unknown font 0 descriptor')
    require(tail[74:140].decode('utf-16-le').rstrip('\0') == 'OlympusLanguage_jpntft', 'wrong JP font descriptor')
    out.extend(tail[:148])
    out.extend(bytes((-len(out)) % 512))
    require(len(out) <= limit, 'strings exceed native loader capacity')
    struct.pack_into('<II', out, 0, en['load_base'] + start, en['load_base'] + end)
    require(parse_strings(out)['strings'] == expected, 'string round-trip mismatch')
    return bytes(out), expected


def make_candidate(stock, translations):
    verify_stock(stock)
    blocks = parse_container(stock)
    require([b['kind'] for b in blocks] == [0x100,0x101,0x106,0x10e,0x102], 'wrong component layout')
    resource = blocks[1]
    require(resource['address'] + 32 == ORIGIN, 'wrong resource origin')
    payload = resource['payload']
    records = parse_resource_directory(payload, ORIGIN)
    require(len(records) == 38, 'wrong resource directory')
    require(sha256(records[28]['decoded']) == JP_FONT_SHA, 'wrong JP font')
    require(max(r['payload_offset'] + r['span'] for r in records) == RESERVE, 'reserve is not after all records')
    require(not any(payload[RESERVE:]), 'reserve is not stock zero fill')
    strings, expected = make_strings(records[5]['decoded'], records[10]['decoded'], translations)
    require(RESERVE + len(strings) <= len(payload), 'candidate leaves resource component')
    require((ORIGIN + RESERVE) % 512 == 0 and len(strings) % 512 == 0, 'native reader alignment mismatch')
    changed = bytearray(payload)
    changed[RESERVE:RESERVE+len(strings)] = strings
    struct.pack_into('<II', changed, JP_DESCRIPTOR, ORIGIN + RESERVE, len(strings))
    new_records = parse_resource_directory(changed, ORIGIN)
    for old, new in zip(records, new_records):
        if old['index'] != 10:
            require(old == new, 'unexpected change to another resource')
    require(new_records[10]['decoded'] == strings, 'new JP record does not resolve')
    at, size = resource['offset'], resource['size']
    head = stock[at:at+32]
    tail = bytearray(stock[at+32+size:at+64+size])
    tail[28:] = bytes(4)
    struct.pack_into('<I', tail, 28, -(sum32(head) + sum32(changed) + sum32(tail)) & 0xffffffff)
    component = head + encode_payload(changed) + tail
    output = stock[:at] + component + stock[at+size+64:]
    checked = parse_container(output)
    require(len(output) == len(stock) and len(checked) == 5, 'container layout changed')
    for i, (old, new) in enumerate(zip(blocks, checked)):
        require(old['header_hex'] == new['header_hex'], 'component header changed')
        if i != 1:
            require(old['stored_sha256'] == new['stored_sha256'], 'non-resource component changed')
    require(checked[1]['payload'] == changed, 'encoded payload mismatch')
    patches = [(JP_DESCRIPTOR, payload[JP_DESCRIPTOR:JP_DESCRIPTOR+8], bytes(changed[JP_DESCRIPTOR:JP_DESCRIPTOR+8])),
               (RESERVE, payload[RESERVE:RESERVE+len(strings)], strings)]
    # Only these two decoded ranges and the resource trailer checksum may differ.
    witness = bytearray(payload)
    for offset, old, new in patches:
        require(witness[offset:offset+len(old)] == old, 'expected bytes mismatch')
        witness[offset:offset+len(new)] = new
    require(witness == changed, 'unlisted change')
    return output, patches, strings, expected
