import sys

def get_filenames():
    print('floodmap set as: ',sys.argv[1])
    print('directory containing domains: ',sys.argv[2])
    print('distance parameter: ',sys.argv[3])
    print('minimum no. of error pixels')
    return sys.argv[1:]