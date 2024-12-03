import numpy as np
from trimesh import PointCloud

from plateau2minecraft.anvil.block import Block

block_type_map = {
    "bldg": Block("minecraft", "stone"),
    "brid": Block("minecraft", "cobblestone"),
    "veg": Block("minecraft", "stone"),
    "frn": Block("minecraft", "bricks"),
    "tran": Block("minecraft", "gray_concrete"),
}


class PointChunk(PointCloud):
    def __init__(self, vertices, feature_type: str):
        super().__init__(vertices)
        self.feature_type = feature_type

    def get_block(self):
        return block_type_map[self.feature_type]

    @staticmethod
    def to_array(point_cloud: PointCloud):
        return np.asarray(point_cloud.vertices)
