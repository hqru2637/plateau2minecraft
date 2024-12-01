// poetry run python -m plateau2minecraft --target "C:\Users\Public\shared\09201_utsunomiya-shi_city_2023_citygml_1_op\udx\bldg\54396753_bldg_6697_op.gml" --output ./result


const index = 543967;

// const maps = [
//   71, 72,
//   61, 62, 63, 64,
//       52, 53, 54
// ]

const maps = [63]

const bldgPath = 'C:\\Users\\Public\\shared\\09201_utsunomiya-shi_city_2023_citygml_1_op\\udx\\bldg\\';
const tranPath = 'C:\\Users\\Public\\shared\\09201_utsunomiya-shi_city_2023_citygml_1_op\\udx\\tran\\';

console.log(
  'poetry run python -m plateau2minecraft --target ' +
  [
    ...maps.map(m => `${bldgPath}${index}${m}_bldg_6697_op.gml`),
    ...maps.map(m => `${tranPath}${index}${m}_tran_6697_op.gml`),
  ].join(' ') +
  ' --output ./utsunomiya_v2'
);
