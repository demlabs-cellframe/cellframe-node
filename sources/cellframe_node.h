#ifndef MAIN_H
#define MAIN_H

#ifdef __ANDROID__
#include <jni.h>
#endif

#ifdef __cplusplus
 extern "C" {
#endif

JNIEXPORT int Java_com_CellframeWallet_Node_cellframeNodeMain(JNIEnv *javaEnv, jobject __unused jobj, jobjectArray argv);
JNIEXPORT int Java_com_CellframeWallet_Node_dapCommonInit(JNIEnv *javaEnv, jobject __unused jobj, jobjectArray argv);
int cellframe_node__cli_Main(int argc, const char *argv[]);
int cellframe_node_tool_Main(int argc, const char **argv);

#ifdef __cplusplus
}
#endif

#endif // MAIN_H
