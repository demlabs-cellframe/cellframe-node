// INodeServiceInterface.aidl
package com.cellframe.node;

import com.cellframe.node.INodeNotifyListner;

interface INodeServiceInterface {
    boolean startNode();
    boolean stopNode();
    boolean setup(boolean from_sratch);
    boolean config(String config_command);
    boolean isNodeRunning();
    void setNotifyLisnter(INodeNotifyListner listner);
    String simpleCliCommand(String cmd);
    String cliCommand(in String[] args);

}