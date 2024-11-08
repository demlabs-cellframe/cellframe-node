package com.cellframe.node;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.os.PowerManager;
import android.os.RemoteException;
import android.preference.PreferenceManager;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.core.app.NotificationBuilderWithBuilderAccessor;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.LinkedList;
import java.util.List;

import com.cellframe.node.Utils;
public class

NodeService extends Service {

    static {
       System.loadLibrary("android-node");
    }

    public interface NJINotifyListener {
        void onNotify(String string);
    }

    private native int nodeMainNative(String sys_dir);
    private native int initConfigs(String base_path, String setup_file_path);
    private native String configure(String base_path, String commad);
    private native void setNotifyListenerNativeCallback(NJINotifyListener JNIListener);
    private native void clearNotifyListenerNativeCallbacks();
    private native byte[] clicommandString(String cmd);
    private native byte[] clicommandArgs(String[] args);
    private native byte[] clicommandJson(String json);
    private native String nodeGetVersion();

    private LinkedList<INodeNotifyListner> notify_listners = new LinkedList<INodeNotifyListner>();


    private  PowerManager.WakeLock wakeLock = null;
    private boolean isServiceStarted = false;
    private String TAG = "cellframe.node.service";
    Thread nodeThread =  null;

    String getNodeWorkingDir(){
        return getFilesDir().getAbsolutePath()+"/opt/";
    }

    void runNode(){
        if (isServiceStarted) return;

        nodeThread = new Thread(new Runnable() {
            @Override
            public void run() {
                setNotifyListenerNativeCallback(new NJINotifyListener() {
                    @Override
                    public void onNotify(String string) {
                        for (INodeNotifyListner listner : notify_listners) {
                            try {
                                listner.onNotify(string);
                            } catch (RemoteException e) {
                                throw new RuntimeException(e);
                            }
                        }
                    }
                });
                nodeMain();
                isServiceStarted = false;
            }
        });

        nodeThread.start();
        isServiceStarted = true;
    }
    private final INodeServiceInterface.Stub binder = new INodeServiceInterface.Stub() {

        @Override
        public boolean startNode() throws RemoteException {
            runNode();
            return isServiceStarted;
        }

        @Override
        public boolean stopNode() throws RemoteException {
            Log.d(TAG, "Call stop");
            if (nodeThread == null || !isServiceStarted) return true;

            clicommandString("exit");

            Log.d(TAG, "interrupting");
            try {
                nodeThread.join();
                Log.d(TAG, "waiting");
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            return true;
        }

        @Override
        public String config(String config_command) throws RemoteException {
            Log.d(TAG, "Call node config");
            return configure(getNodeWorkingDir(), config_command);
        }

        public String nodeVersion() throws RemoteException {
            return nodeGetVersion();
        }


        @Override
        public boolean isNodeRunning(){
            Log.d(TAG, "Call status");
            return isServiceStarted && nodeThread != null;
        }

        @Override
        public void setNotifyLisnter(INodeNotifyListner listner) throws RemoteException {
            notify_listners.add(listner);
        }

        @Override
        public String simpleCliCommand(String cmd) throws RemoteException {
            return new String(clicommandString(cmd), StandardCharsets.US_ASCII);
        }

        public String cliCommand(String args[]) throws RemoteException {
            return new String(clicommandArgs(args), StandardCharsets.US_ASCII);
        }

        public String cliCommandJson(String json) throws RemoteException {
            return new String(clicommandJson(json), StandardCharsets.US_ASCII);
        }

        @Override
        public  boolean setup(boolean from_scratch) {
            Log.d(TAG, "Call setup");

            copyAssetsAndCreateConfigs(from_scratch);
            return true;
        }
    };

    private void startService() {
        Log.d(TAG, "Starting the foreground service task");
        if (isServiceStarted) return;

        Toast.makeText(this, "Service starting its task", Toast.LENGTH_SHORT).show();

        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "CFNode::wakelock");
        wakeLock.acquire();
    }

    private void stopService() {
        Log.d(TAG, "Stopping the foreground service");
        Toast.makeText(this, "Service stopping", Toast.LENGTH_SHORT).show();
        try {
            if (wakeLock != null && wakeLock.isHeld()) wakeLock.release();
            stopForeground(true);
            stopSelf();
        } catch (Exception e) {
            Log.d("CFNode", "Service stopped without being started: " + e.getMessage());
        }
    }
    boolean isFirstStart(Context ctx){
        SharedPreferences sharedPref = ctx.getSharedPreferences("cfnservice", Context.MODE_PRIVATE);
        return sharedPref.getBoolean("first_start",true);
    }

    boolean setNotFirstStart(Context ctx){
        SharedPreferences sharedPref = ctx.getSharedPreferences("cfnservice", Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putBoolean("first_start", true);
        editor.apply();
        return true;
    }


    @Override
    public int onStartCommand(Intent intent, int flags, int startId)
    {
        Log.d(TAG, "onStartCommand executed with startId: " +  startId);
        if (intent == null) {
            Log.d(TAG,
                "with a null intent. It has been probably restarted by the system."
            );
        }
        this.startService();
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return binder;
    };

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "The service has been created".toUpperCase());
        Toast.makeText(this, "Service created", Toast.LENGTH_SHORT).show();
        copyAssetsAndCreateConfigs(isFirstStart(this));

        setNotFirstStart(this);
        startForeground(1, createNotification());
        //initConfigs("lol");
    }

    @Override
    public void onDestroy() {
        stopService();
        Log.d(TAG,"The service has been destroyed".toUpperCase());
        Toast.makeText(this, "Service destroyed", Toast.LENGTH_SHORT).show();
        super.onDestroy();
    }

    private void copyAssetsAndCreateConfigs(boolean from_scratch){
        Log.i(TAG, "Node service initialization: from_scratch="+String.valueOf(from_scratch));

        try {
            if (from_scratch){
                Utils.deleteRecursive(new File(getNodeWorkingDir() + "/etc/"));
                Utils.deleteRecursive(new File(getNodeWorkingDir() + "/share/"));
                Log.i(TAG, "Deleted etc, share dirs");

                Utils.copyDirorfileFromAssetManager(this, "etc", getNodeWorkingDir() + "/etc/");
                Utils.copyDirorfileFromAssetManager(this, "share", getNodeWorkingDir() + "/share/");
                Log.i(TAG, "Populated etc, share dirs from assets");
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        Log.i(TAG, "Asking conftool to setup configuration...");
        initConfigs(getNodeWorkingDir(),getNodeWorkingDir() + "/share/default.setup");
        Log.i(TAG, "Asking conftool to setup configuration... done, ready for operation");
    }

    private void nodeMain(){
        nodeMainNative(getNodeWorkingDir() );
    }

    Notification createNotification()
    {
        String notificationChannelId = "CellframeNodeService Notifications";

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager notificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            NotificationChannel channel = new NotificationChannel(
                    notificationChannelId,
                    "Endless Service notifications channel",
                    NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription("CellframeNodeService Notifications");
            notificationManager.createNotificationChannel(channel);
        }

        Intent intent = getPackageManager().
                getLaunchIntentForPackage("com.cellframe.node");

        Notification.Builder builder = null;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
            builder = new Notification.Builder(this, notificationChannelId);
        else
            builder = new Notification.Builder(this);

        return builder
                .setContentTitle("Cellframe Node")
                .setContentText("Service ready")
                .setContentIntent(null)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setPriority(Notification.PRIORITY_HIGH) // for under android 26 compatibility
                .build();
    }

}
