"""Database class for an ORNL MDF Peregrine build's file structure"""

from myna.core.db import Database
from myna.core import metadata
import os
import numpy as np


class PeregrineDB(Database):
    def __init__(self):
        Database.__init__(self)
        self.description = "ORNL MDF Peregrine build file structure"

    def set_path(self, path):
        """Set the path to the database

        Args:
          path: filepath to the build folder on the Peregrine server
        """
        self.path = os.path.join(path, "Peregrine")
        self.path_dir = self.path

    def exists(self):
        return os.path.isdir(self.path)

    def load(self, metadata_type, part=None, layer=None):
        """Load and return a metadata value from the database

        Implemented metadata loaders:
        - LaserPower
        - LayerThickness
        - Material
        - Preheat
        - SpotSize
        - STL
        - Scanpath
        """

        if metadata_type == metadata.LaserPower:
            datafile = os.path.join(self.path, "simulation", part, "part.npz")
            with np.load(datafile, allow_pickle=True) as data:
                index = [
                    ind
                    for ind, x in enumerate(data["parameter_names"])
                    if x == "Power (W)"
                ][0]
                value = float(data["parameter_values"][index])
            return value

        elif metadata_type == metadata.LayerThickness:
            datafile = os.path.join(self.path, "simulation", "buildmeta.npz")
            with np.load(datafile, allow_pickle=True) as data:
                conversion = 1e-3  # millimeters -> meters
                value = float(data["layer_thickness"] * conversion)
            return value

        elif metadata_type == metadata.Material:
            datafile = os.path.join(self.path, "simulation", "buildmeta.npz")
            with np.load(datafile, allow_pickle=True) as data:
                value = str(data["material"])
            return value

        elif metadata_type == metadata.Preheat:
            datafile = os.path.join(self.path, "simulation", "buildmeta.npz")
            with np.load(datafile, allow_pickle=True) as data:
                index = [
                    ind
                    for ind, x in enumerate(data["metadata_names"])
                    if x == "Target Preheat (°C)"
                ][0]
                value = float(data["metadata_values"][index]) + 273.15
            return value

        elif metadata_type == metadata.SpotSize:
            datafile = os.path.join(self.path, "simulation", part, "part.npz")
            with np.load(datafile, allow_pickle=True) as data:
                index = [
                    ind
                    for ind, x in enumerate(data["parameter_names"])
                    if x == "Spot Size (mm)"
                ][0]
                value = float(data["parameter_values"][index])

            # NOTE: Correct for bug in Peregrine that saved spot size as microns
            # in some files. Assume that if the spot size is greater than 10
            # that it is stored in microns and correct accordingly.
            if value > 10:
                value = value * 1e-3

            return value

        elif metadata_type == metadata.STL:
            file_database = os.path.join(self.path, "simulation", part, f"part.stl")
            return file_database

        elif metadata_type == metadata.Scanpath:
            file_database = os.path.join(
                self.path, "simulation", part, f"{int(layer):07d}.txt"
            )
            return file_database

        else:
            print(f"Error loading: {metadata_type}")
            raise NotImplementedError

    def get_plate_size(self):
        """Load the (x,y) build plate size in meters"""
        with np.load(os.path.join(self.path, "simulation", "buildmeta.npz")) as data:
            value = [x / 1e3 for x in data["actual_size"]]
        return value

    def get_sync_image_size(self):
        """Load the (x,y) image size in pixels"""
        with np.load(os.path.join(self.path, "simulation", "buildmeta.npz")) as data:
            value = data["image_size"]
        return value
