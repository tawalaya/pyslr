class Expression(object):
    def __init__(self,operation,elements,escape=True):
        self.operation = operation
        self.elements=elements
        self.escape=escape

    def withTemplate(self,template,escape=True):
        elems = []
        for elem in self.elements:
            if type(elem) == Expression:
                elems.append(elem.withTemplate(template))
            else:
                elems.append(template.format(elem))
        return Expression(self.operation,elems,escape)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.escape:
            return "({})".format(" {} ".format(self.operation).join(map(escapeStrings,self.elements)))
        else:
            return "({})".format(" {} ".format(self.operation).join(map(str,self.elements)))

def escapeStrings(elem):
    if type(elem) == str:
        return '"{}"'.format(elem)
    else:
        return str(elem)