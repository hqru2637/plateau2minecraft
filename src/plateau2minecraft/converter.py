import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from plateau2minecraft.point import PointChunk

from .anvil import Block, EmptyChunk, EmptyRegion

grass_block = Block("minecraft", "grass_block")
floor_pos_y = 111


class Minecraft:
    def __init__(self) -> None:
        self.regions: dict[str, EmptyRegion] = {}

    def _point_shift(self, points: np.ndarray, x: float, y: float, z: float) -> np.ndarray:
        points += np.array([x, y, z])
        return points

    def _get_region(self, x: int, z: int) -> EmptyRegion:
        region_pos_x = x // 512
        region_pos_z = z // 512
        region_id = f"r.{region_pos_x}.{region_pos_z}.mca"

        if region_id in self.regions:
            return self.regions[region_id]

        region = EmptyRegion(region_pos_x, region_pos_z)
        self.regions[region_id] = region

        return region

    def build_region(self, point_chunk: PointChunk, origin: tuple[float, float] | None = None) -> None:
        points = np.asarray(point_chunk.vertices)

        origin_point = self.get_world_origin(points) if origin is None else origin

        # 点群の中心を原点に移動
        points = self._point_shift(points, -origin_point[0], -origin_point[1], 0)
        # ボクセル中心を原点とする。ボクセルは1m間隔なので、原点を右に0.5m、下に0.5mずらす
        points = self._point_shift(points, 0.5, 0.5, 0)
        # Y軸を反転させて、Minecraftの南北とあわせる
        points[:, 1] *= -1
        points = points.astype(int)

        for point in points:
            # MinecraftとはY-UPの右手系なので、そのように変数を定義する
            x, z, y = point
            region = self._get_region(x, z)
            if (point_chunk.feature_type == "tran"):
                y = floor_pos_y
                region.set_block(point_chunk.get_block(), x, y, z)
            else:
                region.fill(point_chunk.get_block(), x, y, z, x, y - 5, z)

    def _save_region(self, region_id: str, region: EmptyRegion, region_dir: str):
        save_path = f"{region_dir}/{region_id}"
        region.save(save_path)
        return region_id

    def save_regions(self, output: Path):
        # {output}/world_data/region/フォルダの中身を削除
        # フォルダが存在しない場合は、フォルダを作成する
        # フォルダが存在する場合は、フォルダの中身を削除する
        region_dir = f"{output}/world_data/region"
        if os.path.exists(region_dir):
            for file in os.listdir(region_dir):
                os.remove(f"{region_dir}/{file}")
        else:
            os.makedirs(region_dir, exist_ok=True)

        # 並列で region を保存
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._save_region, region_id, region, region_dir): region_id
                for region_id, region in self.regions.items()
            }
            for future in as_completed(futures):
                region_id = futures[future]
                try:
                    print(f"saved: {region_id}")
                except Exception as e:
                    print(f"Error saving region {region_id}: {e}")

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

    def _fill_missing_chunks(self, region: EmptyRegion):
        for i, chunk in enumerate(region.chunks):
            if chunk is None:
                chunk_x = (i % 32) + (region.x * 32)
                chunk_z = (i // 32) + (region.z * 32)
                region.chunks[i] = EmptyChunk(chunk_x, chunk_z)

    def _replace_air_with_grass(self, region: EmptyRegion):
        for chunk in region.chunks:
            if chunk is None:
                continue
            for x in range(16):
                for z in range(16):
                    block = chunk.get_block(x, floor_pos_y, z)
                    if block is None or block.name() == "minecraft:air":
                        chunk.set_block(grass_block, x, floor_pos_y, z)

    def fill_empty_with_grass(self):
        with ThreadPoolExecutor() as executor:
            executor.map(self._process_region, self.regions.values())

    def _process_region(self, region: EmptyRegion):
        self._fill_missing_chunks(region)
        self._replace_air_with_grass(region)
