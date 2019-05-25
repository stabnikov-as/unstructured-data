import bisect


class unstruct_data(object):
    def __init__(self, edges):
        # list of [x1,x2,x3] coordinate lists
        # (list of lists of floats)
        self.points   = []

        # list of coordinates of element vertices
        # (list of lists of ints)
        self.elements = []

        # list of field data lists in points, for example [p,v,u,M]
        # (list of lists of floats)
        self.pointData = []

        # list of field data lists in elements, for example [p,v,u,M]
        # (list of lists of floats)
        self.elemData = []

        # List of names of variables of data in points
        # (list of lists of strings)
        self.pointVariables = []

        # List of names of variables of data in elements
        # (list of lists of strings)
        self.elemVariables = []

        # Number of variables in points
        # (int)
        self.numPointVars = 0

        # Number of variables in elements
        # (int)
        self.numElemVars = 0

        # Line 2 of header in unformatted tecplot file
        # (str)
        self.line2 = ''

        # Line 3 of header in unformatted tecplot file
        # (str)
        self.line3 = ''

        # Number of Elements
        # (int)
        self.numElements = 0

        # Number of Points
        # (int)
        self.numPoints = 0

        # Number of Points with data in them (used while reading tecplot solution file)
        # (int)
        self.numPointsWithData = 0

        # Number of edges in each element
        # (int)
        self.numEdges = edges

        # Minimal edge length in an element
        # (see minimal_distance(self) Function)
        # (float)
        self.minEdgeLength = 0.0


    ## READ FUNCTIONS

    def read_tec(self, filename):
        '''
        Reads unformatted tecplot files
        !!!
        DOESNT READ FIELD DATA, ONLY COORDINATES
        !!!
        :param filename: (str) The name of the file to read
        :return:  no returns
        '''
        print('Reading unformatted tecplot file "{}"'.format(filename))

        isData = False

        with open(filename, 'r') as f_in:
            read_data = f_in.readlines()

        self.__init__(self.getNumEdges())
        ind0 = 0
        if read_data[0].split()[0] in ('Variables', 'variables', 'variables=', 'Variables='):
            self.pointVariables = read_data[0].split()[1:]
            self.pointVariables[0].lstrip(' =')
            ind0 = 1
        self.line2 = read_data[ind0]
        self.line3 = read_data[ind0 + 1]
        element_type = read_data[ind0].split()[6].lstrip('ET=')

        if element_type == 'QUADRILATERAL':
            self.numEdges = 4
        elif element_type == 'TRIANGULAR':
            self.numEdges = 3
        self.numPoints = int(read_data[ind0].split()[2])
        self.numElements = int(read_data[ind0].split()[4])
        if len(read_data[ind0+2].split()) > 3: isData = True
        for i in range(self.getNumPoints()):
            ind = i + 2 + ind0
            line_data = read_data[ind].split()
            for j in range(len(line_data)): line_data[j] = float(line_data[j])
            self.points.append(line_data[:3])
            if isData:
                self.pointData.append(line_data[3:])

        for i in range(self.getNumElements()):
            ind = i + 2 + ind0 + 1 + self.getNumPoints()
            elems = read_data[ind].split()
            for j in range(len(elems)): elems[j] = int(elems[j])
            self.elements.append(elems)

    def read_stl(self, filename):
        '''
        Reads stl file

        assumes that elements are triangular
        Also reads element data and stores it in self.elemData as a list of lists
        :param filename: (str) name of the file to read
        :return: no return
        '''
        print('reading stl file "{}"'.format(filename))
        with open(filename, 'r') as f_in:
            self.numEdges = 3
            self.__init__(self.getNumEdges())
            f_in.readline()
            points_str = []
            i = 0
            while True:
                if i % 1000 == 0: print(i)
                stringData = f_in.readline().split()[2:]
                for j in range(len(stringData)): stringData[j] = float(stringData[j])
                self.elemData.append(stringData)
                if not f_in.readline(): break
                element = []

                for m in range(3):
                    point = f_in.readline().split()[1:]
                    try:
                        index = points_str.index(point) + 1
                    except ValueError:
                        points_str.append(point)
                        self.points.append(point)
                        index = len(self.points)
                    element.append(index)
                f_in.readline()
                f_in.readline()
                self.elements.append(element)
                i += 1
        self.numPoints = len(self.points)
        for i in range(self.getNumPoints()):
            for j in range(len(self.points[i])): self.points[i][j] = float(self.points[i][j])
        self.elemVariables = ['n_x', 'n_y', 'n_z']
        self.numElemVars = len(self.elemVariables)
        self.stringPoints = points_str
        self.numElements = len(self.elements)
        self.line1 = 'zone  N=        {}  E=        {}  F=FEPOINT, ET=TRIANGLE\n'.format(self.getNumPoints(),
                                                                                         self.getNumElements())
        self.line2 = 'T="Block_1         "\n'
        print('Numelements = {}'.format(self.getNumElements()))

    def read_element_data(self, filename):
        '''
        Reads element data from a previously written file
        !!!
            Only works for 3 variables that are most likely n_x, n_y, n_z
        !!!
        :param filename: (str) name of the file to read
        :return: doesn't return anythng
        '''
        if not self.elemData: self.prepare_elem_data()
        print('Reading element data "{}"'.format(filename))
        with open(filename, 'r') as f_out:
            self.numElemVars = int(f_out.readline())
            self.elemVariables = f_out.readline().rstrip('\n').split(', ')
            for i in range(self.getNumElements()):
                varline = f_out.readline().split()
                for j in range(len(varline)): varline[j] = float(varline[j])
                self.elemData[i] = varline


    ## WRITE FUNCTIONS

    def write_tec(self, filename):
        '''
        Write unformatted tecplot file with point data
        :param filename: (str) name of the file to write
        :return:
        '''
        print('Writing unformatted tecplot file "{}"'.format(filename))
        with open(filename, 'w') as f_out:
            varlist = 'variables= X, Y, Z'
            for i in range(3, self.getNumPointVars()):
                varlist += ', '
                varlist += self.pointVariables[i]
            varlist += '\n'
            f_out.write(varlist)
            f_out.write(self.line2)
            f_out.write(self.line3)
            outstring = '{p[0]} {p[1]} {p[2]} '
            for i in range(self.getNumPointVars() - 3):
                outstring += ' {d[' + str(i) + ']}'
            outstring +=  '\n'
            for i in range(self.getNumPoints()):
                if self.pointData:
                    f_out.write(outstring.format(p = self.points[i], d = self.pointData[i]))
                else:
                    f_out.write(outstring.format(p=self.points[i]))
            f_out.write('\n')
            elems_line = ''
            for j in range(self.getNumEdges()):
                elems_line += '  {e[' + str(j) + ']}  '
            elems_line += '\n'
            for i in range(self.getNumElements()):
                f_out.write(elems_line.format(e = self.elements[i]))

    def write_element_data(self, filename):
        '''
        Writes element data from an stl file
        !!!
            Only works for 3 variables that are most likely n_x, n_y, n_z
        !!!
        :param filename: (str) name of the file to write
        :return: doesn't return anythng
        '''
        print('Writing element data "{}"'.format(filename))
        with open(filename, 'w') as f_out:
            f_out.write(str(self.getNumElemVars()))
            f_out.write('\n')
            f_out.write('{p[0]}, {p[1]}, {p[2]}'.format(p = self.elemVariables))
            f_out.write('\n')
            for i in range(self.getNumElements()):
                f_out.write('{p[0]} {p[1]} {p[2]}\n'.format(p = self.elemData[i]))
            f_out.write('\n')


    ## INTERPOLATING FROM TECPLOT

    def add_solution_data(self, filename, tolerance, interface = None):
        '''
        Read formatted tecplot field file from NTS CODE
        !!!
        CURRENTLY TESTED ONLY ON STP SOLUTION WITH SURFACE PRESSURE DATA
        PROBABLY DOESN'T WORK ON OTHER CASES
        !!!
        :param filename: (string) name of file to read
        :param tolerance: (float) tolerance for finding points in dataset
        :param interface: (str), NOT MANDATORY. name of a file containing interfaces connecting tec points with stl points
        :return:
        '''
        print('Reading tecplot file "{}"'.format(filename))

        with open(filename, 'r') as f_in:
            read_data = f_in.readlines()
        stringData = ['#']
        ind = 0
        while stringData[0] == '#':
            stringData = read_data[ind].split()
            ind += 1
        variables = []
        variables.append(stringData[2])
        variables.append(stringData[3])
        while read_data[ind].split()[0] != 'zone':
            variables.append(read_data[ind][:-1])
            ind += 1
        self.pointVariables = variables
        if not interface:
            interface = filename.rstrip('.tec') + '.int'
            isInterf = False
            open(interface, 'w+').close()
        else:
            isInterf = True
        ind_int = 1
        while ind != len(read_data):
            ind, ind_int = self.readZone(ind, ind_int, read_data, tolerance, interface, isInterf)
            ind += 1
            ind_int += 1

    def readZone(self, ind, ind_int, read_data, tolerance, interface, isInterf):
        '''
        Read tecplot zone from NTS CODE solution
        called from add_solution_data function for each zone
        :param ind: (int)  current index in file reading
        :param read_data: (list of strings) list of strings in read tecplot file
        :param tolerance: (float) tolerance to finding a point
        :return:
        '''
        if isInterf:
            int_f = open(interface, 'r')
            interf_data = int_f.readlines()
        else:
            int_f = open(interface, 'a')

        stringData = read_data[ind].split()
        Ni, Nj = int(stringData[2]), int(stringData[4])
        self.numPointVars = len(self.getPointVars())
        ind += 1
        zoneName = read_data[ind].strip('T=" \n')
        if not isInterf: int_f.write('T = {}\n'.format(zoneName))
        print('Scanning zone "{}"'.format(zoneName))
        print('Number of points: {}'.format(Ni * Nj))
        foundPoints = 0
        self.prepare_point_data()
        for i in range(Ni):
            for j in range(Nj):

                if ind % 5000 == 0:
                    print(ind)
                ind += 1
                stringData = read_data[ind].split()
                pointData = stringData[3:]
                floatData = []
                if not isInterf:
                    found, index = self.search_point(stringData[:3], tolerance)
                    if found:
                        foundPoints += 1
                        for variable in range(len(pointData)):
                            floatData.append(float(pointData[variable]))
                        self.pointData[index] = floatData
                        int_f.write('{} {} {}\n'.format(i, j, index))
                    else:
                        print(index)
                else:
                    if int(interf_data[ind_int].split()[0]) == i and int(interf_data[ind_int].split()[1]) == j:
                        index = int(interf_data[ind_int].split()[2])
                        foundPoints += 1
                        for variable in range(len(pointData)):
                            floatData.append(float(pointData[variable]))
                        self.pointData[index] = floatData
                    else:
                        raise Exception('Coordinates in interface file not match grid file')
                    ind_int += 1
        self.numPointsWithData += foundPoints

        print('Found points for {}, out of {} in this zone'.format(foundPoints, Ni*Nj))
        print('Total found points in this geometry: {} out of 78607'.format(self.getNumPointsWithData()))#, self.getNumPoints()))

        return ind, ind_int


    ## UTILITIES

    def prepare_point_data(self):
        '''
        utility function: makes empty list to put point data later on
        :return: no return
        '''
        for point in self.points:
            self.pointData.append([])

    def prepare_elem_data(self):
        '''
        utility function: makes empty list to put elem data later on
        :return: no return
        '''
        for element in self.elements:
            self.elemData.append([])

    def minimal_distance(self):
        '''
        Find minimal distance between two points iterating over all elements
        '''
        minimum = 100.0
        for element in self.elements:
            points = []
            x = []
            y = []
            z = []
            for i in range(3):
                points.append(self.points[element[i] - 1])
            for i in range(3):
                x.append(points[i][0])
                y.append(points[i][1])
                z.append(points[i][2])
            dist1 = ((x[0] - x[1]) ** 2 + (y[0] - y[1]) ** 2 + (z[0] - z[1]) ** 2)**0.5
            dist2 = ((x[1] - x[2]) ** 2 + (y[1] - y[2]) ** 2 + (z[1] - z[2]) ** 2)**0.5
            dist3 = ((x[0] - x[2]) ** 2 + (y[0] - y[2]) ** 2 + (z[0] - z[2]) ** 2)**0.5
            dist = min(dist1, dist2, dist3)
            if dist < minimum: minimum = dist

        self.minEdgeLength = minimum
        return minimum

    def search_point(self, point, tolerance):
        '''
        Search point in dataset, from read Tec file

        point : (list of 3 strings, for example ['1.00000e-4','1.236127836e-6','5.43242e+5']) point from tec file
        tolarance : (float) usually equal to minimal distance between two points times 0.5
        Returns: True if point found and point index
                 False if not found and -2 as index

        '''
        for j in range(len(point)): point[j] = float(point[j])
        x2 = point[0]
        y2 = point[1]
        z2 = point[2]

        for i in range(self.getNumPoints()):
            x1 = self.points[i][0]
            y1 = self.points[i][1]
            z1 = self.points[i][2]
            dist1 = abs(x2 - x1)
            dist2 = abs(y2 - y1)
            dist3 = abs(z2 - z1)
            dist = (dist1**2 + dist2**2 + dist3**2)**0.5
            if dist < tolerance:
                return True, i
        return False, -2

    def calculate_pressure_forces(self, pressure_ind):
        '''
        Calculates pressure forces on the surface
        :param pressure_ind: (int) index of pressure variable in dataset
        :return: (list of floats) Force components
        '''
        F = [0, 0, 0]
        for k in range(self.getNumElements()):
            pres = 0
            pointIndices = [self.elements[k][i] - 1 for i in range(3)]
            points = []
            for i in range(3):
                points.append(self.points[pointIndices[i]])
                pres += self.pointData[pointIndices[i]][pressure_ind]
            pres = pres / 3.0
            a = points[0]
            b = points[1]
            c = points[2]
            norm = self.calculate_norm(a, b, c)
            area = self.calculate_area(a, b, c)
            for i in range(3):
                F[i] += norm[i] * pres * area
        return F

    def calculate_area(self, a, b, c):
        '''
        Calculates area of a triangle
        :param a: (list of 3 floats) coordinates of first point
        :param b: (list of 3 floats) coordinates of second point
        :param c: (list of 3 floats) coordinates of third point
        :return: (float) Area
        '''
        edges = []
        vertices = [a,b,c]
        for i in range(3):
            j = (i + 1) % 3
            edges.append(((vertices[i][0] - vertices[j][0]) ** 2 \
                        + (vertices[i][1] - vertices[j][1]) ** 2 \
                        + (vertices[i][2] - vertices[j][2]) ** 2)** 0.5)
        per = sum(edges) / 2.0
        a1 = per - edges[0]
        b1 = per - edges[1]
        c1 = per - edges[2]
        area = (per*(a1)*(b1)*(c1))**0.5

        return area

    def calculate_norm(self, a, b, c):
        '''
        Calculates normal vector of a triangle
        :param a: (list of 3 floats) coordinates of first point
        :param b: (list of 3 floats) coordinates of second point
        :param c: (list of 3 floats) coordinates of third point
        :return: (float) Area
        '''
        n = []
        vect = [[],[]]
        coord = [a,b,c]
        n = [[],[],[]]
        for i in range(3):
            for j in range(2):
                vect[j].append(coord[j+1][i] - coord[0][i])
        for i in range(3):
            sign = (-1)**i
            indices = [0,1,2]
            indices.remove(i)
            i1 = indices[0]
            i2 = indices[1]
            n[i] = vect[0][i1]*vect[1][i2] - vect[0][i2]*vect[1][i1]
            n[i] *= sign
        mod = 0
        for i in range(3):
            mod += n[i]**2
        mod = mod**0.5
        n = [n[i]/mod for i in range(3)]


        return n


    ## GETTERS

    def getNumElements(self):
        return self.numElements
    def getNumPoints(self):
        return self.numPoints
    def getNumEdges(self):
        return self.numEdges
    def getNumPointVars(self):
        return self.numPointVars
    def getNumElemVars(self):
        return self.numElemVars
    def getNumPointsWithData(self):
        return self.numPointsWithData
    def getElemVars(self):
        return self.elemVariables[:]
    def getPointVars(self):
        return self.pointVariables[:]
    def getMinEdgeLen(self):
        return self.minEdgeLength
