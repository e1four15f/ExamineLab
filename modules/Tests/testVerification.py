def cmp(a, b):
    return (a > b) - (a < b) 

def verifyOut(recvOut, test):
    return True if cmp(recvOut,test) == 0 else False

def verifyMultiple(recv_out_lst, test_lst):
    if len(recv_out_lst) != len(test_lst):
        raise Exception('User out and tests lengths are different [user {UO}, test {tst}]'
                        .format(UO = len(recv_out_lst), tst = len(test_lst)))
    if type(recv_out_lst) != type(test_lst):
        raise Exception('User out and tests types are different [user {UO}, test {tst}]'
                        .format(UO = type(recv_out_lst), tst = type(test_lst)))
    for i in range(len(recv_out_lst)):
        if verifyOut(recv_out_lst[i], test_lst[i]):
            yield (i, True)
        else:
            yield (i, False)
    
