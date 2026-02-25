"""
DICOM pixel-data compression utilities.

Provides DicomCompressor, the single place to register and apply compression
methods for DICOM datasets before transmission.

To add a new compression method:
  1. Add an entry to DicomCompressor.OPTIONS.
  2. Add the corresponding branch in DicomCompressor.compress().
"""


class DicomCompressor:
    """Encapsulates DICOM pixel-data compression for transmission.

    Class attributes
    ----------------
    OPTIONS : dict
        Registry of supported compression methods.
        Key   -> compression key string (used in config / presets)
        Value -> (display label, Transfer Syntax UID string or None)
    """

    # Registry of supported compression methods.
    # Key -> (display label, Transfer Syntax UID or None for uncompressed)
    # Add new entries here to expose additional compression methods to the UI
    # and transmission layer.
    OPTIONS = {
        "none": ("None (Uncompressed)", None),
        "rle":  ("RLE Lossless",        "1.2.840.10008.1.2.5"),
    }

    @classmethod
    def transfer_syntax_uid(cls, compression: str):
        """Return the Transfer Syntax UID string for *compression*, or None.

        Returns None for the "none" key and for unknown keys.
        """
        entry = cls.OPTIONS.get(compression)
        return entry[1] if entry else None

    @staticmethod
    def compress(ds, compression: str):
        """Apply *compression* to a deep copy of *ds* and return it.

        The original dataset is never modified.  Datasets without pixel data
        are returned as-is (deep copy).

        Parameters
        ----------
        ds : pydicom.Dataset
            Dataset to compress.
        compression : str
            Compression key.  Must be a key in DicomCompressor.OPTIONS.

        Returns
        -------
        pydicom.Dataset
            Deep copy of *ds* with pixel data re-encoded according to
            *compression*.

        Raises
        ------
        RuntimeError
            On unknown compression key or encoding failure.
        """
        from copy import deepcopy
        ds_copy = deepcopy(ds)

        if not compression or compression == "none":
            return ds_copy

        if not hasattr(ds_copy, 'PixelData'):
            return ds_copy

        if compression == "rle":
            try:
                from pydicom.uid import RLELossless
                ds_copy.compress(RLELossless)
            except Exception as e:
                raise RuntimeError(f"RLE compression failed: {e}") from e
        else:
            raise RuntimeError(f"Unknown compression option: '{compression}'")

        return ds_copy
