package com.cellframe.node;

import android.content.ComponentName;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.content.res.AssetManager;
import android.os.Build;
import android.os.Bundle;

import com.google.android.material.snackbar.Snackbar;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Environment;
import android.os.IBinder;
import android.os.RemoteException;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.TextView;
import android.widget.Toast;

import androidx.core.app.ActivityCompat;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;

import com.cellframe.node.databinding.ActivityMainBinding;

import java.io.File;
import java.io.IOException;

public class MainActivity extends AppCompatActivity {


    private AppBarConfiguration appBarConfiguration;
    private ActivityMainBinding binding;

    private TextView logtv;

    void addLogLine(CharSequence line)
    {
        logtv.append(line);
        logtv.append("\n");
        binding.scrollView.fullScroll(View.FOCUS_DOWN);

    }
    void processUserInput(CharSequence text) throws RemoteException {
        addLogLine(">> "+text);
        String txt = text.toString();
        if (txt.startsWith("start")) {
            nodeService.startNode();
            addLogLine("[*] Node runnung: " + String.valueOf(nodeService.isNodeRunning()));

        }
        if (txt.startsWith("stop")){
            nodeService.stopNode();
            addLogLine("[*] Node runnung: " + String.valueOf(nodeService.isNodeRunning()));
        }

        if (txt.startsWith("cli")){
            String res = nodeService.simpleCliCommand(txt.substring(txt.indexOf("cli")+3));
            addLogLine(">> " + res);
        }

        if (txt.startsWith("stat")){
            addLogLine("[*] Node runnung: " + String.valueOf(nodeService.isNodeRunning()));
        }

        if (txt.startsWith("tt")){
            String res = nodeService.cliCommand(new String[]{"net","get","status","-net","riemann"});
            addLogLine(">> " + res);
        }

        if (txt.startsWith("setup")){
            nodeService.setup(true);
        }

        if (txt.startsWith("netlist")){
            addLogLine(">> " + nodeService.config("net_list"));
        }
        if (txt.startsWith("config")){
            String cmd = txt.substring(txt.indexOf("config"));
            addLogLine(">> " + nodeService.config("config cellframe-node general debug_mode ensure true"));
            addLogLine(">> " + nodeService.config("network Backbone ensure off"));
            addLogLine(">> " + nodeService.config("network KelVPN ensure off"));
            addLogLine(">> " + nodeService.config("network riemann ensure on"));
        }
    }

    TextView.OnEditorActionListener inputListener = new TextView.OnEditorActionListener() {
        @Override
        public boolean onEditorAction(TextView textView, int i, KeyEvent keyEvent) {
            if (i == EditorInfo.IME_ACTION_SEND) {
                try {
                    processUserInput(textView.getText().toString());
                } catch (RemoteException e) {
                    addLogLine(e.getMessage());

                }
                textView.setText("");
            }
            return true;
        }
    };



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
        logtv = binding.textView;
        logtv.setSingleLine(false);
        binding.editTextText.setOnEditorActionListener(inputListener);

        Intent intent = new Intent();
        intent.setComponent(new ComponentName("com.cellframe.node", "com.cellframe.node.NodeService"));
        if (startForegroundService(intent) != null) {
            addLogLine("[*] CellframeNode Service found, starting up");
        }
        else {addLogLine("[!] CellframeNode not found, please download apk");}

        bindToService();
    }

    private void bindToService() {
        try {
            Intent intent = new Intent();
            intent.setComponent(new ComponentName("com.cellframe.node", "com.cellframe.node.NodeService"));
            bindService(intent, nodeServiceConnection, BIND_AUTO_CREATE);
        } catch (Exception e) {
            Log.i("bindToFiscalService", "e: " + e.getMessage());
            addLogLine("[!!] Error connecting to service.");
        }
    }

    private INodeServiceInterface nodeService = null;
    private ServiceConnection nodeServiceConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName componentName, IBinder iBinder) {
            Log.i("Cli", "onServiceConnected");
            try {
                addLogLine("[*] Connected to CellframeNode Service");

                nodeService = INodeServiceInterface.Stub.asInterface(iBinder);
                addLogLine("[*] Node runnung: " + String.valueOf(nodeService.isNodeRunning()));
                nodeService.setNotifyLisnter(new INodeNotifyListner.Stub() {
                    @Override
                    public void onNotify(String notification_data) throws RemoteException {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                addLogLine("[N]: " + notification_data);
                            }
                        });
                    }


                });
            }catch ( Exception e) {
                Log.i("Cli", "onServiceConnected error: " + e.getMessage());
                addLogLine("[*] Error connecting to CellframeNode service");
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName componentName) {
            addLogLine("[!] Disconnected from cellframe-node-service");
            nodeService = null;
        }
    };


}