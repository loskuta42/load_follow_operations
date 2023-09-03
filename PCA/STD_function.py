from math import sqrt

def standard_deviation1(x,y):
    """Calculation function of the standard deviation for two parameters x,y."""
    num_items = len(x)-1
    # len(x)=len(y)

    c=[]
    for i in range(len(x)):

        d= abs(x[i] - y[i])
        b = d**2
        c.append(b)

    ssd = sum(c)
    variance = ssd/num_items
    std = sqrt(variance)
    #three_std=3*std
    return round(std,2)

def standard_deviation2(lst):
    """Calculation function of the standard deviation for a list (one parameter) """

    num_items = len(lst)
    mean = sum(lst) / num_items
    c=[]
    for x in lst:
        dif = abs(x - mean)
        sq_dif = dif**2
        c.append(sq_dif)

    ssd = sum(c)

    variance = ssd/abs(num_items-1)

    std = sqrt(variance)
    #three_std=3*std

    return round(std,2)

if __name__=="__main__":
    x=[1,2,3,4,5,6]
    y=[7,8,9,10,11,12]

    std= standard_deviation1(x,y)

    print('The standard deviation is {}'.format(std))
    #print('The three standard deviation is {}'.format(three_std))

