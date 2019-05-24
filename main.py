from data_class import *

# Tolerance for serching for points in tecplot file
tolerance = 2.0e-6
# Make an instance of unstructured data
b = unstruct_data(3)


#b.read_stl('surface_A.stl')
b.read_stl('test.stl')
b.write_tec('from_stl_test.tec')
#b.read_tec('from_stl_wing_surface.tec')
#b.write_tec('from_stl_wing_surface.tec')


# Add field (surface) data from structured NTS tecplot files
#b.add_solution_data('tenaca_t-00000001.tec', tolerance)
#b.add_solution_data('tenaca_t-00000002.tec', tolerance)

# Write unstructured teclot file with data
#b.write_tec_data('tec_with_data.tec')


print(b.minimal_distance())