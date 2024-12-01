import os
from pathlib import Path
from typing import Any
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from plateau2minecraft.anvil.empty_chunk import EmptyChunk
from plateau2minecraft.point import Point

from .anvil import Block, EmptyRegion
from .anvil.errors import OutOfBoundsCoordinates

grass_block = Block("minecraft", "grass_block")
floor_pos_y = 112

class Minecraft:
    def __init__(self) -> None:
        self.regions: dict[str, EmptyRegion] = {}

    def _point_shift(self, points: np.ndarray, x: float, y: float, z: float) -> np.ndarray:
        points += np.array([x, y, z])
        return points

    def _split_point_cloud(self, vertices: np.ndarray, region_size: int = 512) -> dict[str, dict[str, Any]]:
        # XYZ座標の取得
        x = vertices[:, 0]
        y = vertices[:, 1]

        # XY座標をブロックサイズで割って、整数値に丸めることでブロックIDを作成
        region_id_x = np.floor(x / region_size).astype(int)
        region_id_y = np.floor(y / region_size).astype(int)

        # 各ブロックIDとそのブロックに含まれる座標を格納するリストを作成
        region_data = {}

        for i, (id_x, id_y) in enumerate(zip(region_id_x, region_id_y)):
            region_id = f"r.{id_x}.{id_y}.mca"
            if region_id not in region_data:
                region_data[region_id] = {
                    'rx': id_x,
                    'ry': id_y,
                    'vertices': []
                }
            region_data[region_id]['vertices'].append(vertices[i])

        return region_data

    def _standardize_vertices(self, splitted: dict[str, dict[str, Any]], region_size: int = 512):
        for region_id, entry in splitted.items():

            # 各頂点を標準化（mod演算を使って座標をblock_sizeで割った余りを取る）
            splitted[region_id]['vertices'] = np.mod(entry['vertices'], region_size)  # verticesを更新

        return splitted


    def build_region(self, point: Point, origin: tuple[float, float] | None = None) -> None:
        points = np.asarray(point.vertices)

        origin_point = self.get_world_origin(points) if origin is None else origin
        # print(f"origin_point: {origin_point}")

        # 点群の中心を原点に移動
        points = self._point_shift(points, -origin_point[0], -origin_point[1], 0)
        # ボクセル中心を原点とする。ボクセルは1m間隔なので、原点を右に0.5m、下に0.5mずらす
        points = self._point_shift(points, 0.5, 0.5, 0)
        # Y軸を反転させて、Minecraftの南北とあわせる
        points[:, 1] *= -1

        # 原点を中心として、x軸方向に512m、y軸方向に512mの領域を作成する
        # 領域ごとに、ボクセルの点群を分割する
        # 分割した点群を、領域ごとに保存する
        blocks = self._split_point_cloud(points)
        standardized_regions = self._standardize_vertices(blocks)

        for region_id, entry in standardized_regions.items():
            region = self.regions[region_id] if region_id in self.regions else EmptyRegion(entry['rx'], entry['ry'])
            print(f"[Region] building ({region.x}, {region.z})")
            points = np.asarray(points).astype(int)
            for row in points:
                x, z, y = row # MinecraftとはY-UPの右手系なので、そのように変数を定義する
                try:
                    if point.feature_type == 'tran':
                        y = floor_pos_y
                    region.set_block(point.get_block(), x, y, z) 
                except OutOfBoundsCoordinates:
                    continue
            self.regions[region_id] = region

    def save_region(self, output: Path):
        # {output}/world_data/region/フォルダの中身を削除
        # フォルダが存在しない場合は、フォルダを作成する
        # フォルダが存在する場合は、フォルダの中身を削除する
        region_dir = f"{output}/world_data/region"
        if os.path.exists(region_dir):
            for file in os.listdir(region_dir):
                os.remove(f"{region_dir}/{file}")
        else:
            os.makedirs(region_dir, exist_ok=True)

        for region_id, region in self.regions.items():
            region.save(f"{region_dir}/{region_id}")
            print(f"saved: {region_id}")

    def get_world_origin(self, points):
        min_x = min(points[:, 0])
        max_x = max(points[:, 0])

        min_y = min(points[:, 1])
        max_y = max(points[:, 1])

        # 中心座標を求める
        center_x = (max_x + min_x) / 2
        center_y = (max_y + min_y) / 2

        # 中心座標を右に0.5m、下に0.5mずらす
        origin_point = (center_x + 0.5, center_y + 0.5)

        return origin_point


    def fill_empty_with_grass(self):
        for region in self.regions.values():
            for i, chunk in enumerate(region.chunks):
                if chunk is None:
                    region.chunks[i] = EmptyChunk(i % 32, i // 32)

                for x in range(16):
                    for z in range(16):
                        block = chunk.get_block(x, floor_pos_y, z)
                        if block is None or block.name() == 'minecraft:air':
                            chunk.set_block(grass_block, x, floor_pos_y, z)
