from data_class import *


b = unstruct_data(3)
#b.read_stl('surface_A.stl')
b.read_stl('test.stl')
#b.read_tec('from_stl_wing_surface.tec')
b.write_tec('from_stl_wing_surface.tec')
#b.add_solution_data('tenaca_t-00000001.tec', 1.0e-8)
#b.add_solution_data('tenaca_t-00000002.tec', 1.0e-8)
#b.write_tec_data('tec_with_data.tec')
print('a')