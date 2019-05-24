from data_class import *

# Tolerance for serching for points in tecplot file
tolerance = 2.0e-6
# Make an instance of unstructured data
b = unstruct_data(3)


#ACTUAL

##################
#     STEP 1     #
##################
#################################
#    READING STL SURFACE FILE   #
#################################

### If STL/SURFACE GRID CHANGED
#b.read_stl('surface_A.stl') # Takes ~ 40 minutes
#b.write_tec('from_stl_wing_surface.tec')
#b.write_element_data('surface_elem_data.tec')

### If STL IS THE SAME
b.read_tec('from_stl_wing_surface.tec')
b.read_element_data('surface_elem_data.tec')
b.write_tec('from_stl_wing_surface1.tec')
b.write_element_data('surface_elem_data1.tec')

##################
#     STEP 2     #
##################
###########################################
#    READING TECPLOT FILE FROM NTS CODE   #
###########################################

### IF NEW FIELDS OR ADDITIONAL FIELD DATA
## Add field (surface) data from structured NTS tecplot files
#b.add_solution_data('tenaca_t-00000001.tec', tolerance) # Takes ~ 1 hour
#b.add_solution_data('tenaca_t-00000002.tec', tolerance) # Takes ~ 1 hour

## Write unstructured teclot file with data
#b.write_tec_data('tec_with_data.tec')



#TESTS

#.read_stl('test.stl')
#b.write_tec_data('from_stl_test.tec')
#b.write_element_data('test_elem_data.tec')
#b.read_element_data('test_elem_data.tec')
#b.write_element_data('test_elem_data1.tec')
