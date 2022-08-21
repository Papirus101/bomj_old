def convert_stats(**kwargs):
    the_list = [k for k in kwargs.keys()]
    the_list2 = [k for k in kwargs.values()]
    for i in range(len(the_list)):
        value2 = the_list2[i]
        value2 = round(value2, 2)
        if value2 >= 100000000000000:
            value2 = str(value2)
            value2 = value2[0]+value2[1]+value2[2]+'.'+value2[3]+value2[4]+'T'
        elif value2 >= 10000000000000:
            value2 = str(value2)
            value2 = value2[0]+value2[1]+'.'+value2[2]+value2[3]+'T'
        elif value2 >= 1000000000000:
            value2 = str(value2)
            value2 = value2[0]+'.'+value2[1]+value2[2]+'T'
        elif value2 >= 100000000000:
            value2 = str(value2)
            value2 = value2[0]+value2[1]+value2[2]+'.'+value2[3]+value2[4]+'B'
        elif value2 >= 10000000000:
            value2 = str(value2)
            value2 = value2[0]+value2[1]+'.'+value2[2]+value2[3]+'B'
        elif value2 >= 1000000000:
            value2 = str(value2)
            value2 = value2[0]+'.'+value2[1]+value2[2]+'B'
        elif value2 >= 100000000:
            value2 = str(value2)
            value2 = value2[0]+value2[1]+value2[2]+'.'+value2[3]+value2[4]+'M'
        elif value2 >= 10000000:
            value2 = str(value2)
            value2 = value2[0]+value2[1]+'.'+value2[2]+value2[3]+'M'
        elif value2 >= 1000000:
            value2 = str(value2)
            value2 = value2[0]+'.'+value2[1]+value2[2]+'M'
        elif value2 >= 100000:
            value2 = str(value2)
            value2 = value2[0]+value2[1]+value2[2]+'.'+value2[3]+value2[4]+'K'
        elif value2 >= 10000:
            value2 = str(value2)
            value2 = value2[0]+value2[1]+'.'+value2[2]+value2[3]+'K'
        elif value2 >= 1000:
            value2 = str(value2)
            value2 = value2[0]+'.'+value2[1]+value2[2]+'K'
        elif value2 < 1000:
            value2 = round(value2, 2)
    return str(value2)