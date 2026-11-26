# SPDX-License-Identifier: Apache-2.0
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reproduce', ROOT / 'tools/reproduce.py')
reproduce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reproduce)


class ReproduceBoundaryTests(unittest.TestCase):
    def test_success_exposes_only_complete_verified_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'new-output'
            data = {'candidate.test': b'candidate bytes', 'reference.test': b'reference bytes'}
            reproduce.write_new_directory(out, data)
            self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()}, data)

    def test_disk_full_during_second_file_exposes_no_final_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'new-output'
            original_open = Path.open

            class DiskFull:
                def __enter__(self):
                    self.stream = original_open(out / '.INCOMPLETE' / 'second.test.partial', 'xb')
                    return self
                def write(self, data):
                    self.stream.write(data[:3])
                    self.stream.flush()
                    raise OSError(28, 'synthetic disk full')
                def __exit__(self, *args):
                    self.stream.close()

            def opened(path, mode='r', *args, **kwargs):
                if path.name == 'second.test.partial' and mode == 'xb':
                    return DiskFull()
                return original_open(path, mode, *args, **kwargs)

            with mock.patch.object(Path, 'open', opened):
                with self.assertRaisesRegex(ValueError, 'incomplete output retained'):
                    reproduce.write_new_directory(out, {'first.test': b'complete', 'second.test': b'longer data'})
            self.assertEqual({p.name for p in out.iterdir()}, {'.INCOMPLETE'})
            self.assertEqual((out / '.INCOMPLETE/second.test.partial').read_bytes(), b'lon')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                reproduce.write_new_directory(out, {})

    def test_corrupted_readback_is_not_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'new-output'
            with mock.patch.object(Path, 'read_bytes', return_value=b'bad'):
                with self.assertRaisesRegex(ValueError, 'hash readback mismatch'):
                    reproduce.write_new_directory(out, {'sample.test': b'yes'})
            self.assertFalse((out / 'sample.test').exists())
            self.assertTrue((out / '.INCOMPLETE/sample.test.partial').is_file())

    def test_input_size_checked_before_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'wrong-size.test'
            source.write_bytes(b'not firmware')
            with mock.patch.object(Path, 'open', side_effect=AssertionError('must not open')):
                with self.assertRaisesRegex(ValueError, 'exact expected size'):
                    reproduce.read_stock(source)

    def test_non_regular_input_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'ordinary file'):
                reproduce.read_stock(Path(tmp))

    def test_input_read_is_bounded_when_opened_file_grows(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'synthetic.test'
            source.write_bytes(b'123456789')
            # Small synthetic gate and stale fstat simulate concurrent growth.
            with mock.patch.object(reproduce, 'STOCK_SIZE', 9):
                original_stat = source.stat()
                with mock.patch.object(reproduce.os, 'fstat', return_value=original_stat):
                    original_open = Path.open
                    def growing(path, *args, **kwargs):
                        with original_open(path, 'ab') as stream:
                            stream.write(b'0123456789')
                        return original_open(path, *args, **kwargs)
                    with mock.patch.object(Path, 'open', growing):
                        with self.assertRaisesRegex(ValueError, 'bounded read'):
                            reproduce.read_stock(source)

    def test_invalid_input_creates_no_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stock = root / 'wrong.bin'
            stock.write_bytes(b'not firmware')
            out = root / 'new-output'
            with contextlib.redirect_stderr(io.StringIO()):
                result = reproduce.main(['--stock', str(stock), '--output-dir', str(out)])
            self.assertEqual(result, 2)
            self.assertFalse(out.exists())

    def test_existing_directory_and_contents_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / 'keep.txt'
            marker.write_bytes(b'preserve')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                reproduce.write_new_directory(root, {'keep.txt': b'changed'})
            self.assertEqual(marker.read_bytes(), b'preserve')

    def test_updater_directory_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('DCOLYMP', 'OMKIT', 'dcolymp', 'omkit'):
                out = Path(tmp) / name
                with self.assertRaisesRegex(ValueError, 'updater/loader'):
                    reproduce.write_new_directory(out, {})
                self.assertFalse(out.exists())
