cmake_minimum_required(VERSION 3.10)
project (1.Stock)

FILE(COPY MyStock.py DESTINATION .)
FILE(COPY MyStockConf.py DESTINATION .)
FILE(COPY MyStockCli.py DESTINATION .)
ADD_TEST(NAME 1.Stock COMMAND ${PYTHON_EXECUTABLE} test.sh )
