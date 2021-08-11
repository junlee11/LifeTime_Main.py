import numpy

s='nan'

def isNumber(s):

    if numpy.isnan(float(s)):
        return s != s
    else:

        try:
            float(s)
            return True
        except ValueError:
            return False

print(isNumber(s))