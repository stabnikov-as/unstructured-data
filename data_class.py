class unstruct_data(object):
    def __init__(self, edges):
        self.points   = [[],[],[]]
        self.elements = []
        for i in range(edges):
            self.elements.append([])
        self.fields = []
        self.line1 = ''
        self.line2 = ''
        self.numElements = 0
        self.numPoints = 0
        self.numEdges = edges

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
            for j in range(3):
                self.points[j].append(float(coords[j]))

        for i in range(self.getNumElements()):
            ind = i + 2 + 1 + self.getNumPoints()
            elems = read_data[ind].split()
            for j in range (self.getNumEdges()):
                self.elements[j].append(elems[j])

    def write_tec(self, filename):
        with open(filename, 'w') as f_out:
            f_out.write(self.line1)
            f_out.write(self.line2)
            for i in range(self.getNumPoints()):
                f_out.write('{} {} {}\n'.format(self.points[0][i], self.points[1][i], self.points[2][i]))
            f_out.write('\n')
            for i in range(self.getNumElements()):
                f_out.write('{} {} {} {}\n'.format(self.elements[0][i], self.elements[1][i], self.elements[2][i], self.elements[3][i]))

    def getNumElements(self):
        return self.numElements
    def getNumPoints(self):
        return self.numPoints
    def getNumEdges(self):
        return self.numEdges



    def read_stl(self, filename):
        pass
