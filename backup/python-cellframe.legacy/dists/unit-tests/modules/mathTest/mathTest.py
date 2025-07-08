from DAP.Core import logIt
from DAP.Core import Math

def summTest():
    res = Math("115792089237316195423570985008687907853269984665640564039457584007913129639935")
    a = Math("115792089237316195423570985008687907853269984665640564039457584007913129639934")
    b = 1
    c = a + b
    if res == c:
        a = Math("115792089237316195423570985008687907853269984665640564000457584007913129639930")
        b = 10000005
        c = a + b
        res = Math("115792089237316195423570985008687907853269984665640564000457584007913139639935")
        if res == c:
            return True
    return False

def subTest():
    res = Math("115792089237316195423570985008687907853269984665640564039457584007913129639934")
    a = Math("115792089237316195423570985008687907853269984665640564039457584007913129639935")
    b = a - 1
    if res == b:
        res=Math("110000000000000000000000000000000000000000000000000000000000000000000000000000")
        a = Math("115792089237316195423570985008687907853269984665640564039457584007913129639935")
        b = Math("5792089237316195423570985008687907853269984665640564039457584007913129639935")
        c = a - b
        if res == c:
            return True
    return False

def multiTest():
    a = Math("6000")
    b = a * 2
    if b == 12000:
        a = Math("501000000000")
        a *= a
        if a == Math("251001000000000000000000"):
            return True
    return False

def divTest():
    a = Math("15.0")
    b = a / Math("2.0")
    c = Math("7.5")
    if b == c:
        a /= a
        if a == Math("1.0"):
            return True
    return False

def compareTest():
    a = Math("3")
    b = 3
    ret = a != b and a < b and b > a
    if ret is False:
        a = Math("115792089237316195423570985008687907853269984665640564039457584007913129639935")
        if a == a:
            b = a - 1
            if a != b and a > b and b < a:
                return True
    return False

def powTest():
    a = Math("3")
    b = Math("2")
    c = Math("9")
    res = a ** b
    return c == res

def floorModTest():
    a = Math("7")
    b = Math("2")
    c = Math("3")
    res = a // b
    return res == c

def remainderModTest():
    a = Math("7")
    b = Math("2")
    c = Math("1")
    res = a % b
    return res == c

def modTest():
    a = Math("5")
    b = Math("3")
    res = divmod(a, b)
    return res[0] == Math("1") and res[1] == Math("2")
def floatTest():
    a = Math("5")
    b = Math("2")
    c = a / b
    res = 5.2
    return float(c) == res

def run_unit_test():
    s_false = "| [FALSE] |"
    s_ok =    "| [ OK ]  |"
    lret = True
    logIt.notice("====================================")
    logIt.notice("| Run test 256 - bit math from SDK |")
    logIt.notice("+----------------------------------+")
    logIt.notice("| Name test              |  Result |")
    logIt.notice("+------------------------+---------+")
    try:
        ret = summTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Summation              "+s_ok)
    else:
        logIt.notice("| Summation              " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = subTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Subtraction            "+s_ok)
    else:
        logIt.notice("| Subtraction            " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = multiTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Multiplication         "+ s_ok)
    else:
        logIt.notice("| Multiplication         " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = divTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Division               " + s_ok)
    else:
        logIt.notice("| Division               " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = compareTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Comparison             " + s_ok)
    else:
        logIt.notice("| Comparison             " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = powTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Pow                    " + s_ok)
    else:
        logIt.notice("| Pow                    " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = floorModTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Floor Mod              " + s_ok)
    else:
        logIt.notice("| Floor Mod              " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = remainderModTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Remainder Mod          " + s_ok)
    else:
        logIt.notice("| Remainder Mod          " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = modTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Mod                    " + s_ok)
    else:
        logIt.notice("| Mod                    " + s_false)
        lret = False
    logIt.notice("+------------------------+---------+")
    try:
        ret = floatTest()
    except:
        ret = False
    if ret is True:
        logIt.notice("| Float                  " + s_ok)
    else:
        logIt.notice("| Float                  " + s_false)
        lret = False

    logIt.notice("====================================")
    return lret

def init():
    logIt.notice("Start test Math plugin")
    modTest()
    # Max value in 256-bit 115792089237316195423570985008687907853269984665640564039457584007913129639935
    test_res = run_unit_test()
    if test_res is True:
        logIt.notice("256-bit math test completed successfully.")
    else:
        logIt.warning("256-bit math test failed.")
    return 0
