// poetry run python -m plateau2minecraft --target "C:\Users\Public\shared\09201_utsunomiya-shi_city_2023_citygml_1_op\udx\bldg\54396753_bldg_6697_op.gml" --output ./result

const isTest = false;

const index = 543967;

const mapsMain = [
  71, 72,
  61, 62, 63, 64,
      52, 53, 54
];

const mapsTest = [63];


const maps = isTest ? mapsTest : mapsMain;
const bldgPath = 'C:\\Users\\Public\\shared\\09201_utsunomiya-shi_city_2023_citygml_1_op\\udx\\bldg\\';
const tranPath = 'C:\\Users\\Public\\shared\\09201_utsunomiya-shi_city_2023_citygml_1_op\\udx\\tran\\';

const command = (
  'poetry run python -m plateau2minecraft --target ' +
  [
    ...maps.map(m => `${bldgPath}${index}${m}_bldg_6697_op.gml`),
    ...maps.map(m => `${tranPath}${index}${m}_tran_6697_op.gml`),
  ].join(' ') +
  ' --output ./utsunomiya_v4'
);
console.log(command);
