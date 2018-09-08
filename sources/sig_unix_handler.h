#pragma once

#undef LOG_TAG
#define LOG_TAG "sig_unix_handler"

extern int sig_unix_handler_init(const char *pid_path);
extern int sig_unix_handler_deinit(void);
