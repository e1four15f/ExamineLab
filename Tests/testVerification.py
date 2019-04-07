def cmp(a, b):
    return (a > b) - (a < b) 

def verifyOut(recvOut, test):
    return True if cmp(recvOut,test) == 0 else False

def verifyMultiple(recvOut_lst, test_lst):
    if len(recvOut_lst) != len(test_lst):
        raise Exception('User out and tests lengths are different [user {UO}, test {tst}]'
                        .format(UO = len(recvOut_lst), tst = len(test_lst)))
    for i in range(len(recvOut_lst)):
        if verifyOut(recvOut_lst[i], test_lst[i]):
            yield True
        else:
            yield (i, recvOut_lst[i], test_lst[i])

    