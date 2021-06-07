# Install script for directory: /home/ubuntu/cellframe-node/cellframe-sdk/modules

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Debug")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/common/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/app-cli/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/chain/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/chain/btc_rpc/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/wallet/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/global-db/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/mempool/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/net/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/channel/chain/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/channel/chain-net/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/channel/chain-net-srv/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/mining/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/net/srv/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/type/dag/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/type/blocks/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/consensus/none/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/consensus/dag-poa/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/consensus/dag-pos/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/service/app/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/service/app-db/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/service/datum/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/service/vpn/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/service/xchange/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/service/stake/cmake_install.cmake")
  include("/home/ubuntu/cellframe-node/build/cellframe-sdk/modules/modules_dynamic/cmake_install.cmake")

endif()

