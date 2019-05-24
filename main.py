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
#    LOADING STL SURFACE FILE   #
#################################

####OPTION 1####
## If STL/SURFACE grid changed##
#b.read_stl('surface_A.stl') # Takes ~ 40 minutes
#b.write_tec('from_stl_wing_surface.tec')
#b.write_element_data('surface_elem_data.tec')

####OPTION 2####
## If stl is the same ###
#b.read_tec('from_stl_wing_surface.tec')


##################
#     STEP 2     #
##################
###########################################
#    LOADING TECPLOT FILE FROM NTS CODE   #
###########################################

####OPTION 1####
## No interfaces calculated yet (New grid, New solution) ##
# !!!!!! WILL OVERWRITE EXISTING INTERFACES !!!!!!!!!
# !!!!!!        NEED TO BACK THEM UP        !!!!!!!!!
#b.add_solution_data('tenaca_t-00000001.tec', tolerance) # Takes ~ 1 hour
#b.add_solution_data('tenaca_t-00000002.tec', tolerance) # Takes ~ 1 hour
## Write unstructured teclot file with field variables data
#b.write_tec('tec_with_data.tec')
########

####OPTION 2####
## Interfaces already calculated (New Solution, Same grid) ##
#b.add_solution_data('tenaca_t-00000001.tec', tolerance, 'tenaca_t-00000001.int')
#b.add_solution_data('tenaca_t-00000002.tec', tolerance, 'tenaca_t-00000002.int')
## Write unstructured teclot file with field variables data
#b.write_tec('tec_with_data.tec')
########

####OPTION 3####
## Just read previously written tec file
b.read_tec('tec_with_data.tec')
########

#b.write_tec('tec_with_data.tec1')
b.read_element_data('surface_elem_data.tec')

##################
#     STEP 3     #
##################
#####################
#    CALCULATIONS   #
#####################

## Calculate pressure force components
# Vel0 = 2.95e+02
# R0 = 1.045e-1
#
F_p = b.calculate_pressure_forces(pressure_ind = 0)
# Cd_p = [F_p[i]*2/R0/Vel0**2 for i in range(3)]
print('F_x = {p[0]}, F_y = {p[1]}, F_z = {p[2]}'.format(p = F_p))
# print('Cp_x = {p[0]}, Cp_y = {p[1]}, Cp_z = {p[2]}'.format(p = Cd_p))




#TESTS

#b.read_stl('test.stl')
#b.write_tec_data('from_stl_test.tec')
#b.write_element_data('test_elem_data.tec')
#b.read_element_data('test_elem_data.tec')
#b.write_element_data('test_elem_data1.tec')
