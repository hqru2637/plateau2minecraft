import argparse
import logging
from pathlib import Path

from plateau2minecraft.anvil.empty_region import EmptyRegion
from plateau2minecraft.converter import Minecraft
from plateau2minecraft.merge_points import merge
from plateau2minecraft.parser import get_triangle_meshs
from plateau2minecraft.point import Point
from plateau2minecraft.voxelizer import voxelize

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _extract_feature_type(file_path: Path) -> str:
    return file_path.name.split("_")[1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        required=True,
        type=Path,
        nargs="*",
        help="the output result encompasses the specified CityGML range",
    )
    parser.add_argument("--output", required=True, type=Path, help="output folder")
    args = parser.parse_args()

    mc = Minecraft()
    target_size = len(args.target)
    points = []
    for i, file_path in enumerate(args.target):
        logging.info("[%s/%s]", i + 1, target_size)
        logging.info("Processing start:\n%s", file_path)
        feature_type = _extract_feature_type(file_path)

        logging.info("Triangulation: %s", file_path.name)
        triangle_mesh = get_triangle_meshs(file_path, feature_type)

        logging.info("Voxelize: %s", file_path.name)
        point_cloud = voxelize(triangle_mesh)

        points.append(Point(point_cloud.vertices, feature_type))

        logging.info("Processing end: %s", file_path.name)

    logging.info("Merging %s points", len(points))
    merged_points = Point.to_array(merge(points))
    logging.info(merged_points.size)

    logging.info("Calculating world origin")
    origin = mc.get_world_origin(merged_points)

    logging.info("Building regions")
    for point in points:
        mc.build_region(point, origin)

    logging.info("Filling grass blocks")
    mc.fill_empty_with_grass()

    logging.info("Saving regions to: %s", args.output)
    mc.save_region(args.output)
