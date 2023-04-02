def get_median(arr):
    '''
    Calculate the median of a sequence.
    :param arr: list
    :return: int or float
    '''
    arr.sort()
    return arr[len(arr)//2] if len(arr) % 2 else (arr[len(arr)//2] + arr[len(arr)//2-1])/2
