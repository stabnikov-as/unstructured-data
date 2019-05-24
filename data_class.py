import bisect


class unstruct_data(object):
    def __init__(self, edges):
        self.points   = []
        self.elements = []
        self.pointData = []
        self.elemData = []
        self.pointVariables = []
        self.elemVariables = []
        self.numPointVars = 0
        self.numElemVars = 0
        self.line1 = ''
        self.line2 = ''
        self.numElements = 0
        self.numPoints = 0
        self.numPointsWithData = 0
        self.numEdges = edges
        self.minEdgeLength = 0.0




    ##READ FUNCTIONS

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

        with open(filename, 'r') as f_in:
            read_data = f_in.readlines()
        element_type = read_data[0].split()[6].lstrip('ET=')

        if element_type == 'QUADRILATERAL':
            self.numEdges = 4
        elif element_type == 'TRIANGULAR':
            self.numEdges = 3

        self.__init__(self.getNumEdges())

        self.line1 = read_data[0]
        self.line2 = read_data[1]
        self.numPoints = int(read_data[0].split()[2])
        self.numElements = int(read_data[0].split()[4])

        for i in range(self.getNumPoints()):
            ind = i + 2
            coords = read_data[ind].split()
            for j in range(3): coords[j] = float(coords[j])
            self.points.append(coords)

        for i in range(self.getNumElements()):
            ind = i + 2 + 1 + self.getNumPoints()
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

    ##WRITE FUNCTIONS

    def write_tec(self, filename):
        '''
        Writes unformatted tecplot file
        !!!
         DOESNT WRITE DATA, ONLY GRID
         !!!
        :param filename: (str) name of the file to write
        :return: doesn't return anythng
        '''
        print('Writing unformatted tecplot file "{}"'.format(filename))
        with open(filename, 'w') as f_out:
            f_out.write(self.line1)
            f_out.write(self.line2)
            for i in range(self.getNumPoints()):
                f_out.write('{p[0]} {p[1]} {p[2]}\n'.format(p = self.points[i]))
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
            f_out.write('{p[0]}, {p[1]}, {p[2]}'.format(p = self.getNumElemVars))
            for i in range(self.getNumElements()):
                f_out.write('{p[0]} {p[1]} {p[2]}\n'.format(p = self.elemData[i]))
            f_out.write('\n')


    def write_tec_data(self, filename):
        '''
        Write unformatted tecplot file with point data
        Probably can replace write_tec(self, filename), but not tested
        :param filename: (str) name of the file to write
        :return:
        '''
        print('Writing unformatted tecplot file "{}"'.format(filename))
        with open(filename, 'w') as f_out:
            varlist = 'variables =X, Y, Z'
            for variable in self.pointVariables:
                varlist += variable
            varlist += '\n'
            f_out.write(varlist)
            f_out.write(self.line1)
            f_out.write(self.line2)
            outstring = '{p[0]} {p[1]} {p[2]}'
            for i in range(len(self.pointVariables)):
                outstring += '{d[' + str(i) + '}'
            outstring +=  '\n'
            for i in range(self.getNumPoints()):
                f_out.write(outstring.format(p = self.points[i], d = self.pointData[i]))
            f_out.write('\n')
            elems_line = ''
            for j in range(self.getNumEdges()):
                elems_line += '  {e[' + str(j) + ']}  '
            elems_line += '\n'
            for i in range(self.getNumElements()):
                f_out.write(elems_line.format(e = self.elements[i]))

    ##INTERPOLATING FROM TECPLOT

    def add_solution_data(self, filename, tolerance):
        '''
        Read formatted tecplot field file from NTS CODE
        !!!
        CURRENTLY TESTED ONLY ON STP SOLUTION WITH SURFACE PRESSURE DATA
        PROBABLY DOESN'T WORK ON OTHER CASES
        !!!
        :param filename: (string) name of file to read
        :param tolerance: (float) tolerance for finding points in dataset
        :return:
        '''
        print('Reading tecplot file "{}"'.format(filename))
        #tolerance = self.getMinEdgeLen()
        with open(filename, 'r') as f_in:
            read_data = f_in.readlines()
        stringData = ['#']
        ind = 0
        while stringData[0] == '#':
            stringData = read_data[ind].split()
            ind += 1
        self.pointVariables.append(stringData[2])
        self.pointVariables.append(stringData[3])
        while read_data[ind].split()[0] != 'zone':
            self.pointVariables.append(read_data[ind][:-1])
            ind += 1
        while ind != len(read_data):
            ind = self.readZone(ind, read_data, tolerance)
            ind += 1

    def readZone(self, ind, read_data, tolerance):
        '''
        Read tecplot zone from NTS CODE solution
        called from add_solution_data function for each zone
        :param ind: (int)  current index in file reading
        :param read_data: (list of strings) list of strings in read tecplot file
        :param tolerance: (float) tolerance to finding a point
        :return:
        '''
        stringData = read_data[ind].split()
        Ni, Nj = int(stringData[2]), int(stringData[4])
        self.numPointVars = len(self.getPointVars())
        ind += 1
        zoneName = read_data[ind].strip('T=" \n')
        print('Scanning zone "{}"'.format(zoneName))
        print('Number of points: {}'.format(Ni * Nj))
        foundPoints = 0
        self.prepare_point_data()
        for i in range(Ni):
            for j in range(Nj):
                if ind % 1000 == 0:
                    print(ind)
                ind += 1
                stringData = read_data[ind].split()

                pointData = stringData[3:]

                found, index = self.search_point(stringData[:3], tolerance)

                if found:
                    foundPoints += 1
                    for variable in range(len(pointData)):
                        self.pointData[index].append(float(pointData[variable]))
                else:
                    print(index)

        self.numPointsWithData += foundPoints

        print('Found points for {}, out of {} in this zone'.format(foundPoints, Ni*Nj))
        print('Total found points in this geometry: {} out of 78607'.format(self.getNumPointsWithData()))#, self.getNumPoints()))
        return ind

    ###UTILITIES

    def prepare_point_data(self):
        '''
        utility function: makes empty list to put point data later on
        :return: no return
        '''
        for point in self.points:
            self.pointData.append([])

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
