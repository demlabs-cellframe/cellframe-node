cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

set (ENABLE_SSL OFF CACHE STRING
   "Enable TLS connections and SCRAM-SHA-1 authentication. Options are
   \"DARWIN\" to use Apple's Secure Transport, \"WINDOWS\" to use Windows
   Secure Channel, \"OPENSSL\", \"LIBRESSL\", \"AUTO\",\ or \"OFF\". These options are
   case-sensitive. The default is \"AUTO\". Note\ that SCRAM-SHA-1 is
   required for authenticating to MongoDB 3.0 and later.")
set (ENABLE_SASL OFF CACHE STRING
   "Enable SASL authentication (Kerberos). Options are \"CYRUS\" to use Cyrus
   SASL, \"SSPI\" to use Windows Native SSPI, \"AUTO\",\ or \"OFF\". These options are case-sensitive.")
set (ENABLE_STATIC AUTO CACHE STRING "Build static libmongoc. Set to ON/AUTO/OFF, default AUTO.")
option (ENABLE_TESTS "Build MongoDB C Driver tests." ON)
option (ENABLE_EXAMPLES "Build MongoDB C Driver examples." ON)
set (ENABLE_SRV AUTO CACHE STRING "Support mongodb+srv URIs. Set to ON/AUTO/OFF, default AUTO.")
option (ENABLE_MAINTAINER_FLAGS "Use strict compiler checks" OFF)
option (ENABLE_AUTOMATIC_INIT_AND_CLEANUP "Enable automatic init and cleanup (GCC only)" ON)
option (ENABLE_CRYPTO_SYSTEM_PROFILE "Use system crypto profile (OpenSSL only)" OFF)
option (ENABLE_TRACING "Turn on verbose debug output" OFF)
option (ENABLE_COVERAGE "Turn on compile options for lcov" OFF)
set (ENABLE_SHM_COUNTERS AUTO CACHE STRING "Enable memory performance counters that use shared memory on Linux. Set to ON/AUTO/OFF, default AUTO.")
set (ENABLE_MONGOC ON CACHE STRING "Whether to build libmongoc. Set to ON/OFF, default ON.")
set (ENABLE_BSON AUTO CACHE STRING "Whether to build libbson. Set to ON/AUTO/SYSTEM, default AUTO.")
set (ENABLE_SNAPPY AUTO CACHE STRING "Enable snappy support. Set to ON/AUTO/OFF, default AUTO.")
set (ENABLE_ZLIB AUTO CACHE STRING "Enable zlib support")
set (ENABLE_ZSTD AUTO CACHE STRING "Enable zstd support. Set to ON/AUTO/OFF, default AUTO.")
option (ENABLE_MAN_PAGES "Build MongoDB C Driver manual pages." OFF)
option (ENABLE_HTML_DOCS "Build MongoDB C Driver HTML documentation." OFF)
option (ENABLE_EXTRA_ALIGNMENT
   "Turn on extra alignment of libbson types. Set to ON/OFF, default ON.\
 Required for the 1.0 ABI but better disabled."
   ON
)
option (ENABLE_RDTSCP
   "Fast performance counters on Intel using the RDTSCP instruction"
   OFF
)
option (ENABLE_APPLE_FRAMEWORK "Build libraries as frameworks on darwin platforms" OFF)
set (ENABLE_ICU AUTO CACHE STRING "Enable ICU support, necessary to use non-ASCII usernames or passwords, default AUTO.")
option (ENABLE_UNINSTALL "Enable creation of uninstall script and associated uninstall build target." ON)
set (ENABLE_CLIENT_SIDE_ENCRYPTION AUTO CACHE STRING "Enable Client-Side Field Level Encryption support. Requires libmongocrypt. Set to ON/AUTO/OFF, default AUTO.")

add_subdirectory(libmongoc)

#target_include_directories(libcurl INTERFACE "libcurl/include/")

#target_include_directories(libcurl PUBLIC
#    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/libcurl/include>
#    $<INSTALL_INTERFACE:include/mylib>
#)
