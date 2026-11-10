import os
import sys
import unittest
from io import BytesIO

import numpy as np
from pydicom import dcmread, dcmwrite
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ImplicitVRLittleEndian, RLELossless, generate_uid
from pynetdicom import AE, evt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dicom_compression import DicomCompressor
from remote import send_grouped_dicom


class TestRemoteCompression(unittest.TestCase):
    def setUp(self):
        self.pixels = np.array([[1, 2], [3, 4]], dtype="<u2")
        self.dataset = Dataset()
        self.dataset.file_meta = FileMetaDataset()
        self.dataset.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
        self.dataset.set_original_encoding(True, True)
        self.dataset.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1.1"
        self.dataset.SOPInstanceUID = generate_uid()
        self.dataset.StudyInstanceUID = generate_uid()
        self.dataset.SeriesInstanceUID = generate_uid()
        self.dataset.Rows = 2
        self.dataset.Columns = 2
        self.dataset.SamplesPerPixel = 1
        self.dataset.PhotometricInterpretation = "MONOCHROME2"
        self.dataset.BitsAllocated = 16
        self.dataset.BitsStored = 16
        self.dataset.HighBit = 15
        self.dataset.PixelRepresentation = 0
        self.dataset.PixelData = self.pixels.tobytes()

    def test_compress_updates_encoding_without_changing_original(self):
        compressed = DicomCompressor.compress(self.dataset, "rle")

        self.assertEqual(compressed.file_meta.TransferSyntaxUID, RLELossless)
        self.assertEqual(compressed.original_encoding, (False, True))
        self.assertTrue(compressed["PixelData"].is_undefined_length)
        np.testing.assert_array_equal(compressed.pixel_array, self.pixels)
        self.assertEqual(self.dataset.original_encoding, (True, True))
        self.assertEqual(
            self.dataset.file_meta.TransferSyntaxUID, ImplicitVRLittleEndian
        )
        self.assertEqual(self.dataset.PixelData, self.pixels.tobytes())

    def _send_to_receiver(self, supported_syntaxes, compression):
        received = []

        def on_store(event):
            dataset = event.dataset
            dataset.file_meta = event.file_meta
            received.append((
                str(event.context.transfer_syntax),
                dataset,
                event.assoc.accepted_contexts,
            ))
            return 0x0000

        receiver = AE(ae_title="RLE_TEST")
        receiver.add_supported_context(
            self.dataset.SOPClassUID, supported_syntaxes
        )
        server = receiver.start_server(
            ("127.0.0.1", 0),
            block=False,
            evt_handlers=[(evt.EVT_C_STORE, on_store)],
        )
        messages = []
        grouped = {
            str(self.dataset.StudyInstanceUID): {
                str(self.dataset.SeriesInstanceUID): [(self.dataset, None)]
            }
        }
        try:
            send_grouped_dicom(
                grouped,
                {
                    "server": "127.0.0.1",
                    "port": server.server_address[1],
                    "calling_ae": "SYNTH_TEST",
                    "called_ae": "RLE_TEST",
                    "skip_c_echo": True,
                    "compression": compression,
                },
                on_message=messages.append,
            )
        finally:
            server.shutdown()
            receiver.shutdown()

        return received, messages

    def test_send_rle_when_receiver_prefers_implicit_little_endian(self):
        received, messages = self._send_to_receiver(
            [ImplicitVRLittleEndian, RLELossless], "rle"
        )

        self.assertEqual(len(received), 1)
        syntax, dataset, contexts = received[0]
        self.assertEqual(syntax, str(RLELossless))
        self.assertTrue(dataset["PixelData"].is_undefined_length)
        np.testing.assert_array_equal(dataset.pixel_array, self.pixels)
        self.assertTrue(any(
            ImplicitVRLittleEndian in context.transfer_syntax
            for context in contexts
        ))
        self.assertTrue(any("RLE Lossless" in message and
                            str(RLELossless) in message for message in messages))
        self.assertEqual(self.dataset.PixelData, self.pixels.tobytes())

    def test_send_rle_rejects_receiver_without_rle(self):
        with self.assertRaisesRegex(ValueError, "RLE Lossless"):
            self._send_to_receiver([ImplicitVRLittleEndian], "rle")

    def test_send_loaded_implicit_dataset_converts_raw_elements(self):
        self.dataset.StudyDescription = "Synthetic encoding regression"
        self.dataset.SmallestImagePixelValue = 1
        stream = BytesIO()
        dcmwrite(stream, self.dataset, enforce_file_format=True)
        stream.seek(0)
        self.dataset = dcmread(stream)
        self.assertTrue(self.dataset.get_item(0x00081030).is_raw)

        received, _ = self._send_to_receiver(
            [ImplicitVRLittleEndian, RLELossless], "rle"
        )

        self.assertEqual(len(received), 1)
        syntax, dataset, _ = received[0]
        self.assertEqual(syntax, str(RLELossless))
        self.assertEqual(dataset.StudyDescription, "Synthetic encoding regression")
        self.assertEqual(dataset.SmallestImagePixelValue, 1)
        np.testing.assert_array_equal(dataset.pixel_array, self.pixels)

    def test_send_without_compression_preserves_native_pixels(self):
        received, _ = self._send_to_receiver([ImplicitVRLittleEndian], "none")

        self.assertEqual(len(received), 1)
        syntax, dataset, _ = received[0]
        self.assertEqual(syntax, str(ImplicitVRLittleEndian))
        self.assertFalse(dataset["PixelData"].is_undefined_length)
        np.testing.assert_array_equal(dataset.pixel_array, self.pixels)


if __name__ == "__main__":
    unittest.main()