"""Synthetic checks for DICOM instance selection and preview orientation."""

import logging
from types import MethodType, SimpleNamespace
import unittest
from unittest.mock import Mock

import numpy as np
from pydicom.dataset import Dataset

from src.appgui import DicomCreatorApp
from src.app_logic import DicomLogicHandler


class TestDicomPreview(unittest.TestCase):
    def test_select_instance_updates_preview_without_changing_tabs(self):
        original = np.array([[1, 4, 9], [16, 25, 36]], dtype=np.uint16)
        second = np.fliplr(original).copy()
        first_dataset = Dataset()
        first_dataset.SOPInstanceUID = "1.2.826.0.1.3680043.10.999.1"
        first_dataset.Rows, first_dataset.Columns = original.shape
        second_dataset = first_dataset.copy()
        second_dataset.SOPInstanceUID = "1.2.826.0.1.3680043.10.999.2"
        app = SimpleNamespace(
            grouped_dicom={"1.2.3": {"1.2.3.4": [(first_dataset, original), (second_dataset, second)]}},
            series_tree=Mock(), image_source="dicom", pixel_array=original,
            image_label=Mock(), container=Mock(), logger=logging.getLogger(__name__),
            _update_image_preview=Mock(), _populate_patient_fields=Mock(),
            _populate_study_fields=Mock(), _populate_series_fields=Mock(),
        )
        app._show_instance_image = MethodType(DicomCreatorApp._show_instance_image, app)
        app.series_tree.selection.return_value = ("instance:1.2.3:1.2.3.4:1",)

        DicomCreatorApp.on_tree_select(app, None)

        np.testing.assert_array_equal(app.pixel_array, second)
        app._update_image_preview.assert_called_once()
        np.testing.assert_array_equal(app._update_image_preview.call_args.args[0], second)
        app.container.select.assert_not_called()
        self.assertEqual(app.selected_study_uid, "1.2.3")
        self.assertEqual(app.selected_series_uid, "1.2.3.4")
        app._populate_patient_fields.assert_called_once_with(second_dataset)
        app._populate_study_fields.assert_called_once_with(second_dataset)
        app._populate_series_fields.assert_called_once_with(second_dataset)

        app.container.tabs.return_value = ("data", "image")
        app.container.tab.side_effect = lambda tab, option: "Image" if tab == "image" else "Load DICOM"
        app._show_instance_image()
        app.container.select.assert_called_once_with(1)

    def test_preview_normalization_preserves_asymmetric_orientation(self):
        pixels = np.array([[0, 257, 1024], [4095, 8191, 65535]], dtype=np.uint16)
        preview = DicomLogicHandler(logging.getLogger(__name__)).process_image_to_uint8(pixels)
        self.assertEqual(preview.shape, pixels.shape)
        self.assertEqual(np.unravel_index(preview.argmax(), preview.shape), (1, 2))
        self.assertEqual(np.unravel_index(preview.argmin(), preview.shape), (0, 0))
        self.assertFalse(np.array_equal(preview, np.fliplr(preview)))


if __name__ == "__main__":
    unittest.main()