import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import storage_commitment


class TestStorageCommitment(unittest.TestCase):
    def setUp(self):
        self.association = Mock()
        self.association.is_established = True
        self.status = Dataset()
        self.status.Status = 0x0000
        self.association.send_n_action.return_value = (self.status, None)
        self.references = [("1.2.840.10008.5.1.4.1.1.2", generate_uid())]
        self.config = {
            "server": "dicom.example.test",
            "port": 104,
            "calling_ae": "DCMCREATOR",
            "called_ae": "PACS",
        }

    @patch("storage_commitment.AE")
    def test_sends_push_model_action_without_tls(self, ae_factory):
        ae_factory.return_value.associate.return_value = self.association
        messages = []
        transaction_uid = generate_uid()

        result = storage_commitment.send_storage_commitment(
            self.references,
            transaction_uid,
            self.config,
            on_message=messages.append,
        )

        self.assertEqual(result, 0x0000)
        ae_factory.return_value.add_requested_context.assert_called_once_with(
            storage_commitment.StorageCommitmentPushModel
        )
        associate_args = ae_factory.return_value.associate.call_args
        self.assertNotIn("tls_args", associate_args.kwargs)
        request, action_type, class_uid, instance_uid = self.association.send_n_action.call_args.args
        self.assertEqual(action_type, 1)
        self.assertEqual(class_uid, storage_commitment.StorageCommitmentPushModel)
        self.assertEqual(instance_uid, storage_commitment.PUSH_MODEL_INSTANCE_UID)
        self.assertEqual(str(request.TransactionUID), transaction_uid)
        self.assertEqual(len(request.ReferencedSOPSequence), 1)
        self.assertEqual(str(request.ReferencedSOPSequence[0].ReferencedSOPClassUID), self.references[0][0])
        self.assertEqual(str(request.ReferencedSOPSequence[0].ReferencedSOPInstanceUID), self.references[0][1])
        self.assertTrue(any("not the final commitment result" in message for message in messages))
        self.association.release.assert_called_once_with()

    @patch("storage_commitment._create_tls_context")
    @patch("storage_commitment.AE")
    def test_uses_shared_tls_context_and_peer_hostname(self, ae_factory, tls_factory):
        ae_factory.return_value.associate.return_value = self.association
        tls_context = SimpleNamespace(check_hostname=True)
        tls_factory.return_value = tls_context
        config = dict(self.config, use_tls=True, tls_config={"verify_server": True})

        storage_commitment.send_storage_commitment(self.references, generate_uid(), config)

        tls_factory.assert_called_once_with(config["tls_config"], None, None)
        self.assertEqual(
            ae_factory.return_value.associate.call_args.kwargs["tls_args"],
            (tls_context, config["server"]),
        )

    @patch("storage_commitment.AE")
    def test_non_success_action_response_raises_and_releases(self, ae_factory):
        ae_factory.return_value.associate.return_value = self.association
        failure = Dataset()
        failure.Status = 0x0122
        failure.ErrorComment = "Unsupported action"
        self.association.send_n_action.return_value = (failure, None)

        with self.assertRaisesRegex(RuntimeError, "0x0122.*Unsupported action"):
            storage_commitment.send_storage_commitment(self.references, generate_uid(), self.config)

        self.association.release.assert_called_once_with()

    @patch("storage_commitment.AE")
    def test_rejects_invalid_uid_before_connecting(self, ae_factory):
        with self.assertRaisesRegex(ValueError, "Transaction UID"):
            storage_commitment.send_storage_commitment(self.references, "not-a-uid", self.config)

        ae_factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()