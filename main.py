from data_class import *

a = unstruct_data(4)
a.read_tec('Grid_tbl.tec')
a.write_tec('grid_clone.tec')
print('a')