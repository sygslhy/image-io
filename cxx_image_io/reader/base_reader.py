from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np


class BaseImageReader(ABC):
    """
    Base interface for all image readers.

    This module defines the abstract base class for image reading strategies.
    Each reader must implement:
    - can_read: determine whether reader supports the given file
    - read:     load image + metadata and return numpy array + metadata object
    """
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
        raise NotImplementedError("can_read must be implemented in subclasses")

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
        raise NotImplementedError("read must be implemented in subclasses")
