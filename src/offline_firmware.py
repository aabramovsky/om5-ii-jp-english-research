# SPDX-License-Identifier: Apache-2.0
"""Read-only OE/container and resource inspection. No encoder or device transport.

Format references: pinned OMKit release/user/omkit_firmware.py and
Caduceus tools/oly_container.py, tools/oly_resource.py (see docs/credits.md).
"""
import hashlib
import struct

PERM = (1, 3, 0, 2, 6, 4, 7, 5, 11, 10, 9, 8, 13, 14, 12, 15)
MAGIC = b'olycompress     '
STOCK_SIZE = 90832896
STOCK_SHA256 = '9de5d77e1d290fa2ed4ebc7d75cee0ed490befbc89566722467d1d421d66d637'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sum32(data):
    require(len(data) % 4 == 0, 'unaligned checksum input')
    return sum(x[0] for x in struct.iter_unpack('<I', data)) & 0xffffffff


def decode_payload(data):
    require(len(data) % 16 == 0, 'unaligned encoded payload')
    out = bytearray(len(data))
    flipped = data.translate(bytes(range(255, -1, -1)))
    for dst, src in enumerate(PERM):
        out[dst::16] = flipped[src::16]
    return bytes(out)


def parse_container(data, expected_model=b'\x14\x80'):
    require(bool(data), 'empty container')
    pos, blocks, kinds = 0, [], set()
    while pos < len(data):
        require(len(data) - pos >= 64, 'truncated component')
        header = data[pos:pos+32]
        require(header[:2] == b'OE', 'invalid OE magic')
        require(header[2:4] == expected_model, 'wrong model (native E148 required)')
        address, size = struct.unpack_from('<II', header, 8)
        version, = struct.unpack_from('<H', header, 16)
        kind, = struct.unpack_from('<H', header, 20)
        require(size > 0 and size % 16 == 0, 'invalid component size')
        end = pos + 32 + size
        require(end + 32 <= len(data), 'component leaves input')
        trailer = data[end:end+32]
        require(header[:28] == trailer[:28] and header[28:] == bytes(4), 'header/trailer mismatch')
        require(kind not in kinds, 'duplicate component type is ambiguous')
        payload = decode_payload(data[pos+32:end]) if kind else data[pos+32:end]
        require((sum32(header) + sum32(payload) + sum32(trailer)) & 0xffffffff == 0, 'invalid checksum')
        blocks.append({'offset': pos, 'kind': kind, 'address': address, 'size': size,
                       'version_raw': version, 'model_bytes': header[2:4].hex(),
                       'header_hex': header.hex(), 'checksum_valid': True,
                       'stored_sha256': sha256(data[pos:end+32]), 'payload_sha256': sha256(payload),
                       'payload': payload})
        kinds.add(kind)
        pos = end + 32
    return blocks


def verify_stock(data):
    require(len(data) == STOCK_SIZE and sha256(data) == STOCK_SHA256,
            'not the pinned native E148/1100 stock; analysis gate closed')


def decompress_lz4(data, expected_size, limit=32*1024*1024):
    """Bounded extraction; NOT a camera loader/stream-alignment compatibility validator."""
    require(0 < expected_size <= limit, 'invalid/oversized expanded length')
    pos, out = 0, bytearray()

    def length(initial):
        nonlocal pos
        value = initial
        if initial == 15:
            while True:
                require(pos < len(data), 'truncated extended length')
                extra = data[pos]
                pos += 1
                value += extra
                require(value <= expected_size, 'length exceeds expanded size')
                if extra != 255:
                    break
        return value

    while pos < len(data):
        token = data[pos]
        pos += 1
        literal = length(token >> 4)
        require(pos + literal <= len(data), 'truncated literals')
        require(len(out) + literal <= expected_size, 'literal output overflow')
        out.extend(data[pos:pos+literal])
        pos += literal
        if pos == len(data):
            break
        require(pos + 2 <= len(data), 'truncated match offset')
        distance = int.from_bytes(data[pos:pos+2], 'little')
        pos += 2
        require(0 < distance <= len(out), 'invalid back-reference')
        count = length(token & 15) + 4
        require(len(out) + count <= expected_size, 'match output overflow')
        # Repeat the available preceding pattern; handles overlapping matches.
        pattern = bytes(out[-distance:])
        out.extend((pattern * ((count + distance - 1)//distance))[:count])
    require(len(out) == expected_size, 'expanded length mismatch')
    return bytes(out)


def parse_resource_directory(payload, origin):
    require(len(payload) >= 16, 'truncated directory')
    first = struct.unpack_from('<I', payload)[0] - origin
    require(16 <= first <= len(payload) and first % 16 == 0, 'invalid directory boundary')
    records, ranges = [], []
    for at in range(0, first, 16):
        pointer, span, flags1, flags2 = struct.unpack_from('<4I', payload, at)
        require(flags1 == flags2 == 0, 'unknown resource flags')
        if not span:
            require(pointer == 0 or first <= pointer-origin <= len(payload), 'invalid empty record')
            continue
        offset = pointer - origin
        require(first <= offset < offset+span <= len(payload), 'resource leaves component')
        require(all(offset+span <= lo or offset >= hi for lo, hi in ranges), 'overlapping records')
        ranges.append((offset, offset+span))
        stored = payload[offset:offset+span]
        packed_size = raw_size = None
        if stored.startswith(MAGIC):
            require(len(stored) >= 32 and stored[24:32] == bytes(8), 'bad compression header')
            packed_size, raw_size = struct.unpack_from('<II', stored, 16)
            require(0 < packed_size <= span-32, 'compressed bytes leave record')
            decoded = decompress_lz4(stored[32:32+packed_size], raw_size)
            padding = stored[32+packed_size:]
        else:
            decoded, padding = stored, b''
        records.append({'index': at//16, 'directory_offset': at, 'source_address': pointer,
                        'payload_offset': offset, 'span': span, 'packed_size': packed_size,
                        'decoded_size': len(decoded), 'decoded_sha256': sha256(decoded),
                        'stored_sha256': sha256(stored), 'padding_values': sorted(set(padding)),
                        'decoded': decoded})
    return records


def parse_strings(data, load_base=0xa407f540, expected_count=4909):
    require(len(data) >= 8, 'truncated string record')
    start, end = struct.unpack_from('<II', data)
    lo, hi = start-load_base, end-load_base
    require(8 <= lo <= hi <= len(data) and lo % 4 == 0 and (hi-lo) % 4 == 0, 'invalid string table bounds')
    require((hi-lo)//4 == expected_count, 'unexpected string count')
    values, offsets = [], []
    for slot in range(lo, hi, 4):
        ptr, = struct.unpack_from('<I', data, slot)
        offset = ptr-load_base
        # Stock E148 stores text BEFORE the pointer table, not after it.
        require(8 <= offset < lo and offset % 2 == 0, 'string pointer outside text area')
        stop = offset
        while stop + 2 <= lo and data[stop:stop+2] != bytes(2):
            stop += 2
        require(stop + 2 <= lo, 'unterminated UTF-16 string')
        text = data[offset:stop].decode('utf-16-le', errors='strict')
        values.append(text)
        offsets.append(offset)
    return {'load_base': load_base, 'table_start': lo, 'table_end': hi,
            'count': len(values), 'strings': values, 'offsets': offsets}
