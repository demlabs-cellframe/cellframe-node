from DAP.Core import logIt
from DAP.Crypto import HashFast
from CellFrame.Chain import ChainAddr
from CellFrame import AppCliServer
import sys, time
import modules.demoCustomCMD as customCMD
import modules.mathTest.mathTest as mathTest


class UnitTest:
    def __init__(self, name, func, result):
        self.name = name
        self.func = func
        self.result = result

    def run(self):
        try:
            result = self.func()
        except Exception as e:
            return False, repr(e)
        if result == self.result:
            return True, None
        else:
            return False, "The function was supposed to return a value of "+str(self.result)+", but returned " \
                                                                                             ""+str(result)+"."

class UnitTests:
    def __init__(self):
        self.test = []
    def registration(self, test):
        self.test.append(test)
    def registration(self, name, func, result):
        test = UnitTest(name, func, result)
        self.test.append(test)

unittest = UnitTests()

def runTestCMD(argv, indexStrReply):
    if len(argv) == 2:
        if argv[1] == "list":
            reply = "The following unit tests are registered:\n"
            i = 1
            for test in unittest.test:
                reply += "\t"+str(i)+". "+test.name+"\n"
                i += 1
            AppCliServer.setReplyText(reply, indexStrReply)
        elif argv[1] == "run":
            len_tests = len(unittest.test)
            logIt.notice("Start testing "+str(len_tests)+" modules (functions).")
            i = 0
            for test in unittest.test:
                i += 1
                logIt.info("["+str(i)+"/"+str(len_tests)+"] "+test.name)
                res = test.run()
                if res[0] == False:
                    logIt.error("Test '"+test.name+"' FAILED! \n Err: "+res[1])
                    reply = "The "+ test.name +" test ended with an error."
                    time.sleep(2)
                    AppCliServer.setReplyText(reply, indexStrReply)
                    return
                else:
                    logIt.notice("Test '"+test.name+"' PASS!")
            reply =  "All tests were successfully completed."
            AppCliServer.setReplyText(reply, indexStrReply)
    else:
        reply = "This function takes a run and a list argument."
        AppCliServer.setReplyText(reply, indexStrReply)

def init():
    logIt.notice("Launching the unit testing plugin.")
    logIt.notice("Registering features to be tested.")
    unittest.registration("Test pass", test_pass, 1)
    unittest.registration("Test for creating a custom CLI command", customCMD.init, 0)
    unittest.registration(
        "Test for getting a HashFast object from a string",
        test_get_hash_fast,
        "0x795327F8B194E24BC6067F5C95DB5B31A74C7CAF28AD74D0A805C960192BD57E")
    unittest.registration(
        "Test for getting an instance of an object of type ChainAddr from a string",
        test_get_chain_addr,
        "mWNv7A43YnqRHCWVJCb2oR1ZaBwaiDQAgZzf3UjXGercDkFwre8z7ShMpsWRRRjRJfdJfQbs8EUqDzKG232a4fpahKBDjfV8ru1LeWTP"
    )
    unittest.registration("256-bit math test", mathTest.run_unit_test, True)
#    unittest.registration("Test FAIL", test_pass, 0)
    AppCliServer.cmdItemCreate("unit_tests", runTestCMD, "Command for working with Unit tests.", 
    """
        This function takes a run parameter and a list
        Parameter:
            * run - runs unit tests sequentially.
            * list - returns a list of registered unit tests.
    """)
    return 0

def test_pass():
    return 1

def test_get_hash_fast():
    ch_hf = HashFast.fromString("abc")
    if ch_hf is not None:
        return False
    ch_hf = HashFast.fromString("0x03FKEN02E0932JF")
    if ch_hf is not None:
        return False
    ch_hf = HashFast.fromString("0x795327F8B194E24BC6067F5C95DB5B31A74C7CAF28AD74D0A805C960192BD57E")
    return str(ch_hf)

def test_get_chain_addr():
    addr = ChainAddr.fromStr("mFJJEF2312AAGIWJIEc1885841")
    if addr is not None:
        return False
    addr = ChainAddr.fromStr("mWNv7A43YnqRHCWVJCb2oR1ZaBwaiDQAgZzf3UjXGercDkFwre8z7ShMpsWRRRjRJfdJfQbs8EUqDzKG232a4fpahKBDjfV8ru1LeWTP")
    return str(addr)
