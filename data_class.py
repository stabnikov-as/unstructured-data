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

    def bisect_search_point(self, point, tolerance):
        for j in range(len(point)): point[j] = float(point[j])
        x2 = point[0]
        y2 = point[1]
        z2 = point[2]

        for i in range(self.getNumPoints()):
            x1 = self.points[i][0]
            y1 = self.points[i][1]
            z1 = self.points[i][2]
            dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5
            if dist < tolerance:
                return True, i
        return False, -2


    def bisect_insert_point(self, point):
        for j in range(len(point)): point[j] = float(point[j])
        'Locate the leftmost value exactly equal to x'
        i = bisect.bisect_left(self.points, point)
        if not (i != len(self.points) and self.points[i] == point):
            self.points.insert(i, point)
        return i


    def read_tec(self, filename):
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

    def write_tec(self, filename):
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


    def read_stl(self, filename):
        print('reading stl file'.format(filename))
        with open(filename, 'r') as f_in:
            read_data = f_in.readlines()

        self.numEdges = 3
        self.__init__(self.getNumEdges())
        read_data.pop(0)
        read_data.pop(-1)
        points_str = []
        self.numElements = len(read_data)//7
        print('Numelements = {}'.format(self.getNumElements()))
        for i in range(self.getNumElements()):
            if i%1000 == 0: print(i)
            stringData = read_data.pop().split()[2:]
            for j in range(len(stringData)): stringData[j] = float(stringData[j])
            self.elemData.append(stringData)
            read_data.pop()
            element = []

            for m in range(3):
                point = read_data.pop().split()[1:]
                try:
                    i = points_str.index(point)
                    element.append(i)

                except ValueError:
                    points_str.append(point)
#                    for j in range(len(point)): point[j] = float(point[j])
                    self.points.append(point)
                    element.append(len(self.points) - 1)
               # self.bisect_insert_point(stringData)
            read_data.pop()
            read_data.pop()
            self.elements.append(element)
        self.numPoints = len(self.points)
        for i in range(self.getNumPoints()):
            for j in range(len(self.points[i])): self.points[i][j] = float(self.points[i][j])
        self.line1 = 'zone  N=        {}  E=        {}  F=FEPOINT, ET=TRIANGLE\n'.format(self.getNumPoints(), self.getNumElements())
        self.line2 =  'T="Block_1         "\n'
        self.elemVariables = ['S_x', 'S_y', 'S_z']
        self.numElemVars = len(self.elemVariables)
        #self.points.sort()

    def prepare_point_data(self):
        for point in self.points:
            self.pointData.append([])

    def add_solution_data(self, filename, tolerance):
        print('Reading tecplot file "{}"'.format(filename))
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
        stringData = read_data[ind].split()
        Ni, Nj = int(stringData[2]), int(stringData[4])
        self.numPointVars = len(self.getPointVars())
        ind += 1
        zoneName = read_data[ind].strip('T=" \n')
        print('Scanning zone "{}"'.format(zoneName))
        print('Number of points: {}'.format(Ni*Nj))
        foundPoints = 0
        self.prepare_point_data()
        for i in range(Ni):
            for j in range(Nj):
                if ind % 1000 == 0: print(ind)
                ind += 1
                stringData = read_data[ind].split()

                pointData = stringData[-1]

                found, i = self.bisect_search_point(stringData[:-1], tolerance)

                if found:
                    foundPoints += 1
                    self.pointData[i].append(pointData)
                else:
                    print(i)


        self.numPointsWithData += foundPoints

        print('Found points for {}, out of {} in this zone'.format(foundPoints, Ni*Nj))
        print('Total found points in this geometry: {} out of {}'.format(self.getNumPointsWithData(), self.getNumPoints()))

        return ind

    def write_tec_data(self, filename):
        print('Writing unformatted tecplot file "{}"'.format(filename))
        with open(filename, 'w') as f_out:
            f_out.write('variables = p')
            f_out.write(self.line1)
            f_out.write(self.line2)
            for i in range(self.getNumPoints()):
                f_out.write('{p[0]} {p[1]} {p[2]} {d[0]}\n'.format(p = self.points[i], d = self.pointData[i] ))
            f_out.write('\n')
            elems_line = ''
            for j in range(self.getNumEdges()):
                elems_line += '  {e[' + str(j) + ']}  '
            elems_line += '\n'
            for i in range(self.getNumElements()):
                f_out.write(elems_line.format(e = self.elements[i]))

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
