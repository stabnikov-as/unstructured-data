import bisect

class point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.x = y
        self.x = z
    def distance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)**0.5



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
        self.numEdges = edges

    def bisect_insert_point(self, point):
        for j in range(len(point)): point[j] = float(point[j])
        'Locate the leftmost value exactly equal to x'
        i = bisect.bisect_left(self.points, point)
        if not (i != len(self.points) and self.points[i] == point):
            self.points.insert(i, point)
        return i


    def read_tec(self, filename):
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


    def write_elem_data(self, filename):
        with open(filename, 'w') as f_out:
            for i in range(self.getNumElemVars()):
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
    def getElemVars(self):
        return self.elemVariables[:]
    def getPointVars(self):
        return self.pointVariables[:]



    def read_stl(self, filename):
        with open(filename, 'r') as f_in:
            read_data = f_in.readlines()

        self.numEdges = 3
        self.__init__(self.getNumEdges())
        elementsTmp = []
        read_data.pop(0)
        read_data.pop(-1)
        self.numElements = len(read_data)//7
        print('Numelements = {}'.format(self.getNumElements()))
        for i in range(self.getNumElements()):
            if i%1000 == 0: print(i)
            stringData = read_data.pop().split()[2:]
            for j in range(len(stringData)): stringData[j] = float(stringData[j])
            self.elemData.append(stringData)
            read_data.pop()
            element = []

            for point in range(3):
                stringData = read_data.pop().split()[1:]
                # try:
                #     pointIndex = self.points.index(stringData)
                # except ValueError:
                #     self.points.append(stringData)
                #     pointIndex = len(self.points) - 1
                pointIndex = self.bisect_insert_point(stringData)
                element.append(stringData)
            read_data.pop()
            read_data.pop()
            elementsTmp.append(element)
        for element in elementsTmp:
            elemIndex = []
            for i in range(3):
                pointIndex = self.bisect_insert_point(element[i])
                elemIndex.append(pointIndex+1)
            self.elements.append(elemIndex)
        self.numPoints = len(self.points)
        for i in range(self.getNumPoints()):
            for j in range(len(self.points[i])): self.points[i][j] = float(self.points[i][j])
        self.line1 = 'zone  N=        {}  E=        {}  F=FEPOINT, ET=TRIANGLE\n'.format(self.getNumPoints(), self.getNumElements())
        self.line2 =  'T="Block_1         "\n'
        self.elemVariables = ['S_x', 'S_y', 'S_z']
        self.numElemVars = len(self.elemVariables)

    def add_solution_data(self, filename, tolerance):
        with open(filename, 'r') as f_in:
            read_data = f_in.readlines()
        string_data = ['#']
        ind = 0
        while string_data[0] == '#':
            string_data = read_data[ind].split()
            ind += 1
        self.pointVariables.append(string_data[2])
        self.pointVariables.append(string_data[3])
        while read_data[ind].split()[0] != 'zone':
            self.pointVariables.append(read_data[ind][:-1])
            ind += 1
        ind += 1
        Ni, Nj = read_data[ind].split()[2], read_data[ind].split()[4]
        self.numPointVars = len(self.getPointVariables)
        ind += 1
        zoneName = read_data[ind]
        foundPoints = 0
        for i in range(Ni):
            for j in range(Nj):
                ind += 1
                string.data = read_data[ind].split()
                x = float(string_data[0])
                y = float(string_data[1])
                z = float(string_data[2])

                point = Point(x, y, z)

                pointData = string_data[3:]

                for i in range(self.getNumPoints()):
                    vertex = self.points[i]
                    point2 = Point(vertex[0], vertex[1], vertex[2])

                    if point.distance(point2) <= tolerance:
                        found_points += 1
                        self.pointData[i].append(pointData)
                        break





        print(1)
