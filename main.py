

class unstruct_data(object, edges):
    def __init__(self):
        self.points   = [[],[],[]]
        self.elements = [[],[],[]]
        self.fields = []
        self.line1 = ''
        self.line2 = ''
        self.numElements = 0
        self.numPoints = 0
        self.numEdges = edges

    def read_tec(self, filename):
        with open(filename, 'r') as f_in:
            read_data = f_in.readlines()
        self.line1 = read_data[0]
        self.line2 = read_data[1]
        self.numPoints = read_data[0].split()[2]
        self.numElements = read_data[0].split()[4]
        element_type = read_data[0].split()[6].lstrip('ET=')

        if element_type == 'QUADRILATERAL':
            self.numEdges = 4
        elif element_type == 'TRIANGULAR':
            self.numEdges = 3


        for i in range(self.numPoints):
            coords = read_data[i+2].split()
            for j in range (3):
                self.points[j].append(coords[j])

        for i in range(self.numElements):
            elems = read_data[i+2].split()
            for j in range (self.getNumEdges()):
                self.points[j].append(elems[j])


    def getNumElements(self):
        return self.numElements
    def getNumPoints(self):
        return self.numPoints
    def getNumEdges(self):
        return self.numElements



    def read_stl(self, filename):
        pass


sad
