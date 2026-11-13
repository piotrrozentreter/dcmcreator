"""Tkinter receiver tests using only synthetic data and a loopback listener."""

import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

from src.dicom_receiver_tab import DicomReceiverTab


class TestDicomReceiverTab(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk display unavailable: {error}")
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)
        self.tab = DicomReceiverTab(frame, self.root, None)
        self.addCleanup(self.tab.close)
        self.tab._variables["output"].set(self.directory.name)

    def test_defaults_are_loopback_and_tls_disabled(self):
        settings = self.tab._configuration()
        self.assertEqual(settings["host"], "127.0.0.1")
        self.assertEqual(settings["ae_title"], "DCMCREATOR_SCP")
        self.assertFalse(settings["prefer_rle"])
        self.assertNotIn("tls_cert", settings)

    def test_rle_preference_is_forwarded_to_receiver(self):
        self.tab.prefer_rle.set(True)
        self.assertTrue(self.tab._configuration()["prefer_rle"])

    def test_sender_lists_and_tls_configuration(self):
        self.tab._variables["callers"].set("ACUO_TEST, SECOND_AE, ")
        self.tab._variables["ips"].set("192.0.2.1, 192.0.2.2")
        self.tab.use_tls.set(True)
        self.tab._variables["cert"].set("cert.pem")
        self.tab._variables["key"].set("key.pem")
        self.tab._variables["ca"].set("ca.pem")
        settings = self.tab._configuration()
        self.assertEqual(settings["allowed_calling_aes"], ["ACUO_TEST", "SECOND_AE"])
        self.assertEqual(settings["allowed_ips"], ["192.0.2.1", "192.0.2.2"])
        self.assertEqual(settings["tls_ca"], "ca.pem")

    @patch("src.dicom_receiver_tab.messagebox.showerror")
    def test_invalid_port_and_incomplete_tls_do_not_start(self, showerror):
        self.tab._variables["port"].set("0")
        self.tab.start()
        self.assertFalse(self.tab.receiver.running)
        self.tab._variables["port"].set("11112")
        self.tab.use_tls.set(True)
        self.tab.start()
        self.assertEqual(showerror.call_count, 2)

    def test_background_start_stop_and_controls(self):
        with patch.object(self.tab, "_configuration", return_value={
            "output_dir": self.directory.name, "port": 0
        }):
            self.tab.start()
        self.tab._worker.join(5)
        self.assertFalse(self.tab._worker.is_alive())
        self.tab._refresh()
        self.assertTrue(self.tab.receiver.running)
        self.assertTrue(self.tab.start_button.instate(["disabled"]))
        self.assertTrue(self.tab.status.get().startswith("Listening"))
        self.tab.stop()
        self.tab._worker.join(5)
        self.tab._refresh()
        self.assertFalse(self.tab.receiver.running)
        self.assertFalse(self.tab.start_button.instate(["disabled"]))
        self.assertEqual(self.tab.status.get(), "Stopped")

    @patch("src.dicom_receiver_tab.messagebox.showerror")
    def test_worker_failure_is_reported_on_refresh(self, showerror):
        with patch.object(self.tab.receiver, "start", side_effect=OSError("port occupied")):
            self.tab.start()
            self.tab._worker.join(5)
        self.tab._refresh()
        self.assertEqual(self.tab.status.get(), "Error")
        self.assertFalse(self.tab.start_button.instate(["disabled"]))
        showerror.assert_called_once()

    def test_log_is_bounded_and_clear_preserves_counters(self):
        for index in range(600):
            self.tab.receiver._emit("test", detail=str(index))
        for _ in range(3):
            self.tab._refresh()
        self.assertEqual(len(self.tab.tree.get_children()), 500)
        self.tab._clear()
        self.assertEqual(len(self.tab.tree.get_children()), 0)
        self.assertIn("Received: 0", self.tab.summary.get())

    def test_destroy_stops_listener_and_cancels_poll(self):
        self.tab.receiver.start(self.directory.name, port=0)
        self.tab.frame.destroy()
        self.assertFalse(self.tab.receiver.running)
        self.assertTrue(self.tab._closed)


if __name__ == "__main__":
    unittest.main()