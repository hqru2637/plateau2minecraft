import sys

is_test = "test" in sys.argv

index = 543967

maps_main = [
    71, 72,
    61, 62, 63, 64,
        52, 53, 54
]

maps_test = [63]

maps = maps_test if is_test else maps_main
bldg_path = "C:\\Users\\Public\\shared\\09201_utsunomiya-shi_city_2023_citygml_1_op\\udx\\bldg\\"
tran_path = "C:\\Users\\Public\\shared\\09201_utsunomiya-shi_city_2023_citygml_1_op\\udx\\tran\\"

command = (
    "poetry run python -m plateau2minecraft --target " +
    " ".join(f"{bldg_path}{index}{m}_bldg_6697_op.gml" for m in maps) + " " +
    " ".join(f"{tran_path}{index}{m}_tran_6697_op.gml" for m in maps) + " " +
    "--output ./utsunomiya_map"
)

print(command)
