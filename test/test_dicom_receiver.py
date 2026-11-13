"""Synthetic Storage SCP tests; no archive or external executable required."""

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import queue
import socket
import ssl
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.encaps import encapsulate
from pydicom.uid import (ExplicitVRLittleEndian, ImplicitVRLittleEndian,
                         JPEGBaseline8Bit, RLELossless, generate_uid)
from pynetdicom import AE
from pynetdicom.sop_class import SecondaryCaptureImageStorage, Verification

from src.dicom_receiver import DicomReceiver


class TestDicomReceiver(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.receiver = DicomReceiver()
        self.addCleanup(self.receiver.stop)
        self.receiver.start(self.directory.name, port=0)

    def dataset(self, syntax=ExplicitVRLittleEndian):
        dataset = Dataset()
        dataset.SOPClassUID = SecondaryCaptureImageStorage
        dataset.SOPInstanceUID = generate_uid()
        dataset.StudyInstanceUID = generate_uid()
        dataset.SeriesInstanceUID = generate_uid()
        dataset.PatientName = "SYNTHETIC^TEST"
        dataset.PatientID = "TEST-ONLY"
        dataset.Modality = "OT"
        dataset.Rows = dataset.Columns = dataset.SamplesPerPixel = 1
        dataset.PhotometricInterpretation = "MONOCHROME2"
        dataset.BitsAllocated = dataset.BitsStored = 8
        dataset.HighBit = 7
        dataset.PixelRepresentation = 0
        dataset.PixelData = b"\x00\x00"
        dataset.file_meta = FileMetaDataset()
        dataset.file_meta.TransferSyntaxUID = syntax
        return dataset

    def connect(self, called="DCMCREATOR_SCP", calling="SYNTHETIC_SCU",
                syntax=ExplicitVRLittleEndian):
        application = AE(ae_title=calling)
        application.add_requested_context(Verification)
        application.add_requested_context(SecondaryCaptureImageStorage, syntax)
        application.acse_timeout = 2
        application.dimse_timeout = 2
        association = application.associate("127.0.0.1", self.receiver.address[1],
                                            ae_title=called)
        self.addCleanup(lambda: association.release() if association.is_established else None)
        return association

    def test_receive_echo_store_readback_and_duplicate(self):
        association = self.connect()
        self.assertTrue(association.is_established)
        self.assertEqual(association.send_c_echo().Status, 0)
        dataset = self.dataset()
        expected = np.array([[1, 257, 1024], [4095, 8191, 65535]], dtype="<u2")
        dataset.Rows, dataset.Columns = expected.shape
        dataset.BitsAllocated = dataset.BitsStored = 16
        dataset.HighBit = 15
        dataset.PixelData = expected.tobytes()
        self.assertEqual(association.send_c_store(dataset).Status, 0)
        self.assertEqual(association.send_c_store(dataset).Status, 0)
        files = list(Path(self.directory.name).glob("*.dcm"))
        self.assertEqual(len(files), 2)
        for path in files:
            saved = pydicom.dcmread(path)
            self.assertEqual(saved.SOPInstanceUID, dataset.SOPInstanceUID)
            self.assertEqual(saved.file_meta.TransferSyntaxUID, ExplicitVRLittleEndian)
            self.assertEqual(saved.PixelData, dataset.PixelData)
            np.testing.assert_array_equal(saved.pixel_array, expected)
        self.assertEqual(self.receiver.stats["received"], 2)
        self.assertEqual(self.receiver.stats["bytes"], sum(path.stat().st_size for path in files))

    def test_compressed_payload_is_preserved_without_codec(self):
        association = self.connect(syntax=JPEGBaseline8Bit)
        dataset = self.dataset(JPEGBaseline8Bit)
        dataset.PixelData = encapsulate([b"synthetic-encapsulated-payload"])
        dataset["PixelData"].is_undefined_length = True
        self.assertEqual(association.send_c_store(dataset).Status, 0)
        saved = pydicom.dcmread(next(Path(self.directory.name).glob("*.dcm")))
        self.assertEqual(saved.file_meta.TransferSyntaxUID, JPEGBaseline8Bit)
        self.assertEqual(saved.PixelData, dataset.PixelData)

    def test_rle_preference_negotiates_and_preserves_real_compressed_pixels(self):
        self.receiver.stop()
        self.receiver.start(self.directory.name, port=0, prefer_rle=True)
        association = self.connect(syntax=[ImplicitVRLittleEndian, ExplicitVRLittleEndian, RLELossless])
        self.assertTrue(association.is_established)
        storage = [context for context in association.accepted_contexts
                   if context.abstract_syntax == SecondaryCaptureImageStorage]
        self.assertEqual(storage[0].transfer_syntax, [RLELossless])
        dataset = self.dataset()
        expected = np.array([[1, 257, 513, 1024, 4095],
                     [17, 300, 777, 2048, 8191],
                     [33, 511, 1000, 16384, 65535]], dtype="<u2")
        dataset.Rows, dataset.Columns = expected.shape
        dataset.BitsAllocated = dataset.BitsStored = 16
        dataset.HighBit = 15
        dataset.PixelData = expected.tobytes()
        dataset.compress(RLELossless)
        compressed = dataset.PixelData
        self.assertEqual(association.send_c_store(dataset).Status, 0)
        saved = pydicom.dcmread(next(Path(self.directory.name).glob("*.dcm")))
        self.assertEqual(saved.file_meta.TransferSyntaxUID, RLELossless)
        self.assertEqual(saved.PixelData, compressed)
        np.testing.assert_array_equal(saved.pixel_array, expected)
        self.assertFalse(np.array_equal(saved.pixel_array, np.fliplr(expected)))
        self.assertFalse(np.array_equal(saved.pixel_array, np.flipud(expected)))
        context = self.next_event("context")
        while context["transfer_syntax"] != str(RLELossless):
            context = self.next_event("context")
        self.assertIn(f"Context ID: {storage[0].context_id}", context["detail"])

    def test_default_preference_is_unchanged(self):
        association = self.connect(syntax=[RLELossless, ExplicitVRLittleEndian, ImplicitVRLittleEndian])
        storage = [context for context in association.accepted_contexts
                   if context.abstract_syntax == SecondaryCaptureImageStorage]
        self.assertEqual(storage[0].transfer_syntax, [ImplicitVRLittleEndian])

    def test_rle_preference_allows_uncompressed_only_sender(self):
        self.receiver.stop()
        self.receiver.start(self.directory.name, port=0, prefer_rle=True)
        association = self.connect()
        self.assertTrue(association.is_established)
        self.assertEqual(association.send_c_store(self.dataset()).Status, 0)

    def test_rle_only_context_is_supported_without_preference(self):
        association = self.connect(syntax=RLELossless)
        self.assertTrue(association.is_established)
        dataset = self.dataset()
        dataset.compress(RLELossless)
        self.assertEqual(association.send_c_store(dataset).Status, 0)

    def event(self, dataset):
        return SimpleNamespace(
            dataset=dataset, file_meta=dataset.file_meta,
            request=SimpleNamespace(AffectedSOPInstanceUID=dataset.SOPInstanceUID,
                                    AffectedSOPClassUID=dataset.SOPClassUID),
            context=SimpleNamespace(abstract_syntax=dataset.SOPClassUID,
                                    transfer_syntax=ExplicitVRLittleEndian),
            assoc=SimpleNamespace(requestor=SimpleNamespace(address="127.0.0.1",
                                                            ae_title="SYNTHETIC_SCU")))

    def test_invalid_uid_cannot_escape_output_directory(self):
        event = self.event(self.dataset())
        event.dataset = SimpleNamespace(SOPInstanceUID="../escape")
        self.assertEqual(self.receiver._handle_store(event), 0xC210)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [])
        self.assertEqual(self.receiver.stats["failed"], 1)

    def test_uid_validation_rejects_noncanonical_values(self):
        for value in ("", "1.02.3", "1..2", "1.2/3", "1." + "2" * 64):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.receiver._uid(value)

    def test_missing_uid_is_rejected(self):
        dataset = self.dataset()
        event = self.event(dataset)
        del dataset.SOPInstanceUID
        self.assertEqual(self.receiver._handle_store(event), 0xC210)

    def test_mismatched_uid_is_rejected(self):
        event = self.event(self.dataset())
        event.request.AffectedSOPInstanceUID = generate_uid()
        self.assertEqual(self.receiver._handle_store(event), 0xA900)

    def test_write_failure_returns_failure_and_removes_partial_file(self):
        with patch("src.dicom_receiver.pydicom.dcmwrite", side_effect=OSError("disk full")):
            self.assertEqual(self.receiver._handle_store(self.event(self.dataset())), 0xA700)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [])
        self.assertEqual(self.receiver.stats["received"], 0)

    def test_wrong_called_ae_is_rejected(self):
        self.assertFalse(self.connect(called="WRONG_AE").is_established)

    def next_event(self, kind):
        for _ in range(100):
            record = self.receiver.events.get(timeout=2)
            if record["kind"] == kind:
                return record
        self.fail(f"Event not received: {kind}")

    def test_tcp_connection_is_visible_before_association_request(self):
        with socket.create_connection(self.receiver.address, timeout=2):
            record = self.next_event("connected")
            self.assertEqual(record["peer"], "127.0.0.1")
            self.assertEqual(record["detail"], "TCP connection opened")
        self.next_event("disconnected")

    def test_association_stage_events(self):
        association = self.connect(calling="AcuoMed")
        self.assertTrue(association.is_established)
        self.next_event("connected")
        request = self.next_event("requested")
        self.assertEqual(request["calling_ae"], "AcuoMed")
        self.assertEqual(request["detail"], "Called AE: DCMCREATOR_SCP")
        accepted = self.next_event("association")
        self.assertEqual(accepted["detail"], "Accepted contexts: 2")
        association.release()
        self.next_event("released")

    def test_rejection_includes_dicom_reason_codes(self):
        self.assertFalse(self.connect(called="WRONG_AE").is_established)
        rejected = self.next_event("rejected")
        self.assertEqual(rejected["detail"],
                         "Association rejected: result=1, source=1, diagnostic=7")

    def test_calling_ae_restriction(self):
        self.receiver.stop()
        self.receiver.start(self.directory.name, port=0, allowed_calling_aes=["ALLOWED"])
        self.assertFalse(self.connect().is_established)
        self.assertTrue(self.connect(calling="ALLOWED").is_established)

    def test_source_ip_restriction(self):
        self.receiver.stop()
        self.receiver.start(self.directory.name, port=0, allowed_ips=["192.0.2.1"])
        self.assertFalse(self.connect().is_established)

    def test_allowed_source_ip_is_accepted(self):
        self.receiver.stop()
        self.receiver.start(self.directory.name, port=0, allowed_ips=["127.0.0.1"])
        self.assertTrue(self.connect().is_established)

    def test_parallel_senders_store_distinct_files(self):
        port = self.receiver.address[1]

        def send_instance(index):
            application = AE(ae_title=f"SYNTHETIC_{index}")
            application.add_requested_context(SecondaryCaptureImageStorage, ExplicitVRLittleEndian)
            association = application.associate("127.0.0.1", port, ae_title="DCMCREATOR_SCP")
            if not association.is_established:
                return None
            try:
                return association.send_c_store(self.dataset()).Status
            finally:
                association.release()

        with ThreadPoolExecutor(max_workers=3) as executor:
            statuses = list(executor.map(send_instance, range(3)))
        self.assertEqual(statuses, [0, 0, 0])
        self.assertEqual(self.receiver.stats["received"], 3)
        self.assertEqual(len(list(Path(self.directory.name).glob("*.dcm"))), 3)

    def test_unsupported_sop_class_is_not_negotiated(self):
        application = AE(ae_title="SYNTHETIC_SCU")
        application.add_requested_context("1.2.826.0.1.3680043.10.999.1")
        association = application.associate("127.0.0.1", self.receiver.address[1],
                                            ae_title="DCMCREATOR_SCP")
        self.addCleanup(lambda: association.release() if association.is_established else None)
        self.assertEqual(association.accepted_contexts, [])

    def test_stop_with_active_connection_and_restart(self):
        association = self.connect()
        self.receiver.stop()
        self.assertFalse(self.receiver.running)
        self.assertFalse(association.is_established)
        self.receiver.stop()
        self.receiver.start(self.directory.name, port=0)
        self.assertTrue(self.connect().is_established)

    def test_occupied_port_leaves_receiver_stopped(self):
        self.receiver.stop()
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen()
            with self.assertRaises(OSError):
                self.receiver.start(self.directory.name, port=occupied.getsockname()[1])
        self.assertFalse(self.receiver.running)

    def test_bounded_events_do_not_block_or_include_demographics(self):
        self.receiver.events = queue.Queue(maxsize=1)
        self.receiver._emit("test")
        self.receiver._emit("test")
        self.assertEqual(self.receiver.stats["dropped_events"], 1)
        record = self.receiver.events.get_nowait()
        self.assertNotIn("PatientName", record)

    def test_tls_configuration_requires_certificate_and_key(self):
        self.receiver.stop()
        with self.assertRaisesRegex(ValueError, "certificate and private key"):
            self.receiver.start(self.directory.name, port=0, tls_ca="missing.pem")

    @patch("src.dicom_receiver.AE")
    @patch("src.dicom_receiver.ssl.SSLContext")
    def test_tls_policy_requires_client_certificate_when_ca_configured(self, context_factory, ae_factory):
        self.receiver.stop()
        context = context_factory.return_value
        self.receiver.start(self.directory.name, port=0, tls_cert="cert.pem",
                            tls_key="key.pem", tls_ca="ca.pem")
        context_factory.assert_called_once_with(ssl.PROTOCOL_TLS_SERVER)
        self.assertEqual(context.minimum_version, ssl.TLSVersion.TLSv1_2)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        context.load_verify_locations.assert_called_once_with(cafile="ca.pem")
        self.assertIs(ae_factory.return_value.start_server.call_args.kwargs["ssl_context"], context)
        self.receiver.stop()

    def test_invalid_tls_files_fail_closed(self):
        self.receiver.stop()
        with self.assertRaises(OSError):
            self.receiver.start(self.directory.name, port=0,
                                tls_cert="nonexistent-cert.pem", tls_key="nonexistent-key.pem")
        self.assertFalse(self.receiver.running)

    def test_configuration_validation(self):
        self.receiver.stop()
        for settings in ({"port": -1}, {"ae_title": "X" * 17},
                         {"ae_title": "BAD\\AE"}, {"host": "not-an-ip"}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                self.receiver.start(self.directory.name, **settings)


if __name__ == "__main__":
    unittest.main()