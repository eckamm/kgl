import sys
from pprint import pprint


def data1d_get_slice(data1d, shape, dim_idx, dim_offset):
    span = 1
    for i in range(dim_idx):
        span *= shape[i]
    stride = span * shape[dim_idx]

    idx = 0
    offset = dim_offset * span
    result = []
    while 1:
        for i in range(span):
            data1d_offset = idx + i + offset
            result.append((data1d_offset, data1d[data1d_offset]))
        idx += stride
        if idx >= len(data1d):
            break
    return result


def data1d_to_nested(shape, data1d):
    assert len(shape) == 3
    nested = []
    for z in range(shape[2]):
        layer = []
        for y in range(shape[1]):
            row = []
            for x in range(shape[0]):
                row.append(data1d[x + y*shape[0] + z*shape[0]*shape[1]])
            layer.append("".join(row))
        nested.append(layer)
    return nested 


def nested_to_data1d(nested):
    data1d = []
    for layer in nested:
        for row in layer:
            for col in row:
                data1d.append(col)
    return "".join(data1d)
 

def nested_op(nested, target="top", action="add", fillchar=" "):
    assert action in ("add", "delete")
    assert target in ("top", "bottom", "left", "right")
    xnested = []
    for layer in nested:
        xlayer = []

        for row in layer:
            xrow = []
            for col in row:
                xrow.append(col)

            if action=="add" and target=="left":
                xrow.insert(0, fillchar)
            elif action=="add" and target=="right":
                xrow.append(fillchar)
            elif action=="delete" and target=="left":
                del xrow[0]
            elif action=="delete" and target=="right":
                del xrow[-1]

            xlayer.append("".join(xrow))

        if action=="add" and target=="top":
            xlayer.insert(0, fillchar*len(xrow))
        elif action=="add" and target=="bottom":
            xlayer.append(fillchar*len(xrow))
        elif action=="delete" and target=="top":
            del xlayer[0]
        elif action=="delete" and target=="bottom":
            del xlayer[-1]

        xnested.append(xlayer)

    shape = (len(xnested[0][0]), len(xnested[0]), len(xnested))
    return xnested, shape



class Data1D:
    def __init__(self, shape, data1d):
        self.shape = shape
        self.data1d = data1d

    def dump(self, fp=sys.stdout):
        for z in range(self.shape[2]):
            for y in range(self.shape[1]):
                line = []
                for x in range(self.shape[0]):
                    line.append(self.data1d[x + y*self.shape[0] + z*self.shape[0]*self.shape[1]])
                print >>fp, "".join(line)
            print >>fp

    def is_empty(self, target, offset, empty_chars=" "):
        assert target in ("column", "row")
        if target == "column":
            dim_idx = 0
        else:
            dim_idx = 1
        t = data1d_get_slice(self.data1d, self.shape, dim_idx, offset)
        t2 = set([val for idx, val in t if val]).difference(set(empty_chars))
        if t2:
            return False
        else:
            return True

    def change_size(self, target, action, fillchar=" "):
        """
        e.g.
            .change("top", "delete")
            .change("right", "add", "x")
        """
        nested = data1d_to_nested(self.shape, self.data1d)
        nested, self.shape = nested_op(nested, target=target, action=action, fillchar=fillchar)
        self.data1d = nested_to_data1d(nested)


def test():
    data1d = '0123456789abcdefghijklmn'
    shape = (3, 4, 2) # x  y  z
    # constant x -> columns
    print (data1d_get_slice(data1d, shape, 0, 0))
    print (data1d_get_slice(data1d, shape, 0, 1))
    print (data1d_get_slice(data1d, shape, 0, 2))
    # constant y -> rows
    print (data1d_get_slice(data1d, shape, 1, 0))
    print (data1d_get_slice(data1d, shape, 1, 1))
    print (data1d_get_slice(data1d, shape, 1, 2))
    print (data1d_get_slice(data1d, shape, 1, 3))
    # constant z -> layers
    print (data1d_get_slice(data1d, shape, 2, 0))
    print (data1d_get_slice(data1d, shape, 2, 1))
    print "=" * 32
    o = Data1D(shape, data1d)
    o.dump()

    o.change_size("top", "add", "+")
    o.dump()
    o.change_size("left", "add", "+")
    o.dump()
    o.change_size("bottom", "add", "+")
    o.dump()
    o.change_size("right", "add", "+")
    o.dump()

    print o.is_empty("row", 0)
    o.change_size("top", "add", " ")
    print o.is_empty("row", 0)
    return

    nested = data1d_to_nested(shape, data1d)
    pprint(nested, width=20)
    xdata1d = nested_to_data1d(data1d)
    assert xdata1d == data1d

    xnested, xshape = nested_op(nested, target="top", action="add")
    assert xshape == (3, 5, 2)
    print xshape
    pprint(xnested, width=20)

    xnested, xshape = nested_op(xnested, target="bottom", action="add")
    assert xshape == (3, 6, 2)
    print xshape
    pprint(xnested, width=20)

    xnested, xshape = nested_op(xnested, target="left", action="add")
    assert xshape == (4, 6, 2)
    print xshape
    pprint(xnested, width=20)

    xnested, xshape = nested_op(xnested, target="right", action="add")
    assert xshape == (5, 6, 2)
    print xshape
    pprint(xnested, width=20)

    xnested, xshape = nested_op(xnested, target="top", action="delete")
    assert xshape == (5, 5, 2)
    print xshape
    pprint(xnested, width=20)

    xnested, xshape = nested_op(xnested, target="top", action="add", fillchar="x")
    assert xshape == (5, 6, 2)
    print xshape
    pprint(xnested, width=20)



if __name__=="__main__":
    test()

