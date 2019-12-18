#ifndef MAIN_H
#define MAIN_H

#ifdef __cplusplus
 extern "C" {
#endif

#ifdef __ANDROID__

#define LOG_PATH

int cellframe_node_Main(int argc, const char **argv);
int cellframe_node__cli_Main(int argc, const char *argv[]);
int cellframe_node_tool_Main(int argc, const char **argv);

#endif

#ifdef __cplusplus
}
#endif

#endif // MAIN_H
