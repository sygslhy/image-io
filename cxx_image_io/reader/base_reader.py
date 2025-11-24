"""
Base interface for all image readers.

This module defines the abstract base class for image reading strategies.
Each reader must implement:
    - can_read: determine whether reader supports the given file
    - read:     load image + metadata and return numpy array + metadata object
"""

from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np

class BaseImageReader(ABC):
    """Abstract base class for image readers."""

    @abstractmethod
    def can_read(self, image_path: Path) -> bool:
        """
        Check whether this reader supports the given file type.

        Parameters
        ----------
        image_path : Path
            Path to the image file.

        Returns
        -------
        bool
            True if the reader supports this file.
        """
        pass

    @abstractmethod
    def read(self, image_path: Path, metadata_path: Path = None) -> (np.ndarray, object):
        """
        Read the image and metadata.

        Parameters
        ----------
        image_path : Path
            File to load.
        metadata_path : Path, optional
            Path to metadata sidecar file.

        Returns
        -------
        np.ndarray
            Loaded image in numpy array.
        object
            Metadata object (ImageMetadata or Metadata depending on backend)
        """
        pass
