#include <android/log.h>
#include <time.h>
#include <unistd.h>
#include <jni.h>
#include "../cellframe-node.h"
#include "../../conftool/cellframe-node-config.h"


std::string jstring2string(JNIEnv *env,
                           jstring jStr) {
    if (!jStr)
        return "";

    const jclass stringClass = env->GetObjectClass(jStr);
    const jmethodID getBytes = env->GetMethodID(stringClass, "getBytes", "(Ljava/lang/String;)[B");
    const jbyteArray stringJbytes = (jbyteArray) env->CallObjectMethod(jStr, getBytes, env->NewStringUTF("UTF-8"));

    size_t length = (size_t) env->GetArrayLength(stringJbytes);
    jbyte* pBytes = env->GetByteArrayElements(stringJbytes, NULL);

    std::string ret = std::string((char *)pBytes, length);
    env->ReleaseByteArrayElements(stringJbytes, pBytes, JNI_ABORT);

    env->DeleteLocalRef(stringJbytes);
    env->DeleteLocalRef(stringClass);
    return ret;
}

//notify listner logic
static JavaVM *jvm = nullptr;
class NotifyListenerStore {
public:
    NotifyListenerStore(jweak pJobject, jmethodID pID){
            store_Wlistener=pJobject;
            store_method = pID;
    }

    jweak store_Wlistener=NULL;
    jmethodID store_method = NULL;
};

std::vector<NotifyListenerStore *> listeners_vector;
JNIEnv *store_env;

extern "C"
JNIEXPORT void JNICALL
Java_com_cellframe_node_NodeService_setNotifyListenerNativeCallback(JNIEnv *env, jobject instance,
                                                                   jobject listener) {

    env->GetJavaVM(&jvm); //store jvm reference for later call

    store_env = env;

    jweak store_Wlistener = env->NewWeakGlobalRef(listener);
    jclass clazz = env->GetObjectClass(store_Wlistener);

    jmethodID store_method = env->GetMethodID(clazz, "onNotify", "(Ljava/lang/String;)V");

    NotifyListenerStore *tmpt = new NotifyListenerStore(store_Wlistener, store_method);

    listeners_vector.push_back(tmpt);

    __android_log_print(ANDROID_LOG_VERBOSE, "GetEnv:", " Subscribe to Listener  OK \n");
    if (nullptr == store_method) return;
}

extern "C"
JNIEXPORT void JNICALL
Java_com_cellframe_node_NodeService_clearNotifyListenerNativeCallbacks(JNIEnv *env, jobject instance) {
    if (!listeners_vector.empty()) {
        for (auto &i: listeners_vector) {
            env->DeleteWeakGlobalRef(i->store_Wlistener);
            i->store_method = NULL;
        }
        listeners_vector.clear();
    }
}

void callOnNotify(JNIEnv *env, const _jstring *message_)
{
    if (!listeners_vector.empty()) {
        for (auto &i: listeners_vector) {
            env->CallVoidMethod(i->store_Wlistener,
                                i->store_method, message_);
        }
    }
}

bool notifycallback(const char *data){
    __android_log_print(ANDROID_LOG_ERROR, "CellframeNotify", "%s" , data);

    __android_log_print(ANDROID_LOG_VERBOSE, "GetEnv:", " start Callback  to JNL [%d]  \n", data);
    JNIEnv *g_env;
    if (NULL == jvm) {
        __android_log_print(ANDROID_LOG_ERROR, "GetEnv:", "  No VM  \n");
        return false;
    }
    //  double check it's all ok
    JavaVMAttachArgs args;
    args.version = JNI_VERSION_1_6; // set your JNI version
    args.name = NULL; // you might want to give the java thread a name
    args.group = NULL; // you might want to assign the java thread to a ThreadGroup

    int getEnvStat = jvm->GetEnv((void **) &g_env, JNI_VERSION_1_6);

    if (getEnvStat == JNI_EDETACHED) {
        if (jvm->AttachCurrentThread(&g_env, &args) != 0) {
            __android_log_print(ANDROID_LOG_ERROR, "GetEnv:", " Failed to attach");
        }
    } else if (getEnvStat == JNI_OK) {
        __android_log_print(ANDROID_LOG_VERBOSE, "GetEnv:", " JNI_OK");
    } else if (getEnvStat == JNI_EVERSION) {
        __android_log_print(ANDROID_LOG_ERROR, "GetEnv:", " version not supported");
    }

    jstring message = g_env->NewStringUTF(data);//

    callOnNotify(g_env, message);

    if (g_env->ExceptionCheck()) {
        g_env->ExceptionDescribe();
    }

    if (getEnvStat == JNI_EDETACHED) {
        jvm->DetachCurrentThread();
    }

    return true;
}

extern "C" JNIEXPORT jint JNICALL
Java_com_cellframe_node_NodeService_nodeMainNative(
        JNIEnv* env,
        jobject  instance , jstring system_dir)
{
    set_global_sys_dir(jstring2string(env,system_dir).c_str());
    dap_notify_data_set_user_callback(notifycallback);
    int res= main(0,0);
    Java_com_cellframe_node_NodeService_clearNotifyListenerNativeCallbacks(env, instance);
    return res;
}


extern "C" JNIEXPORT jint JNICALL Java_com_cellframe_node_NodeService_initConfigs(
        JNIEnv* env,
        jobject /* this */, jstring base_path, jstring setup_file_path)
{
    try {
        conftool::populate_variables(jstring2string(env, base_path));
        return conftool::init_configs(jstring2string(env, setup_file_path),0,true);
    }
    catch (std::exception e){
        __android_log_print(ANDROID_LOG_ERROR, "CellframeNodeConfig", "Error in configuration init: %s" , e.what());
    }
    return -1;
}



extern "C" JNIEXPORT jint JNICALL Java_com_cellframe_node_NodeService_configure(
        JNIEnv* env,
        jobject /* this */, jstring base_path, jstring config_command)
{
    try {
        conftool::populate_variables(jstring2string(env, base_path));

        std::vector < std::unique_ptr<CAbstractScriptCommand>> commands;
        commands.push_back(conftool::parse_line_to_cmd(jstring2string(env, config_command), 0, 0));
        return conftool::run_commands(commands,false, 0);
    }
    catch (std::exception e){
        __android_log_print(ANDROID_LOG_ERROR, "CellframeNodeConfig", "Error in configuration init: %s" , e.what());
    }
    return -1;
}

extern "C" JNIEXPORT jbyteArray JNICALL Java_com_cellframe_node_NodeService_clicommandArgs(JNIEnv *env, jobject instance,  jobjectArray stringArray)
{
    int stringCount = env->GetArrayLength(stringArray);
    std::vector< char *> args;

    for (int i=0; i<stringCount; i++) {
        jstring string = (jstring) (env->GetObjectArrayElement(stringArray, i));
        const char *rawString = env->GetStringUTFChars(string, 0);
        args.push_back((char *)rawString);
    }
    args.push_back(0);

    char * cli_answer = dap_cli_exec(args.size(),&args[0]);
    int reslen = strlen(cli_answer);
    jbyteArray arr = env->NewByteArray(reslen);
    env->SetByteArrayRegion(arr,0,reslen, (jbyte*)cli_answer);

    return arr;
}

extern "C" JNIEXPORT jbyteArray JNICALL Java_com_cellframe_node_NodeService_clicommandString(JNIEnv *env, jobject instance, jstring cmd)
{
    std::string rcmd = jstring2string(env, cmd);

    std::vector<char *> args;
    std::istringstream iss(rcmd);

    std::string token;
    while(iss >> token) {
        char *arg = new char[token.size() + 1];
        copy(token.begin(), token.end(), arg);
        arg[token.size()] = '\0';
        args.push_back(arg);
    }
    args.push_back(0);

    char * cli_answer = dap_cli_exec(args.size(),&args[0]);
    int reslen = strlen(cli_answer);
    jbyteArray arr = env->NewByteArray(reslen);
    env->SetByteArrayRegion(arr,0,reslen, (jbyte*)cli_answer);

    for(size_t i = 0; i < args.size(); i++)
        delete[] args[i];

    return arr;
}
