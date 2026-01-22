package com.cellframe.node;

import android.content.Context;
import android.content.res.AssetManager;
import android.os.Environment;
import android.util.Log;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

public class Utils {
    public static String copyDirorfileFromAssetManager(Context ctx, String arg_assetDir, String arg_destinationDir) throws IOException
    {
        File sd_path = Environment.getExternalStorageDirectory();
        String dest_dir_path = arg_destinationDir;
        File dest_dir = new File(dest_dir_path);

        createDir(dest_dir);

        AssetManager asset_manager = ctx.getAssets();
        String[] files = asset_manager.list(arg_assetDir);

        for (int i = 0; i < files.length; i++)
        {

            String abs_asset_file_path = addTrailingSlash(arg_assetDir) + files[i];
            String sub_files[] = asset_manager.list(abs_asset_file_path);

            if (sub_files.length == 0)
            {
                // It is a file
                String dest_file_path = addTrailingSlash(dest_dir_path) + files[i];
                copyAssetFile(ctx,abs_asset_file_path, dest_file_path);
            } else
            {
                // It is a sub directory
                copyDirorfileFromAssetManager(ctx, abs_asset_file_path, addTrailingSlash(arg_destinationDir) + files[i]);
            }
        }

        return dest_dir_path;
    }


    public static void copyAssetFile(Context ctx, String assetFilePath, String destinationFilePath) throws IOException
    {
        InputStream in = ctx.getAssets().open(assetFilePath);
        OutputStream out = new FileOutputStream(destinationFilePath);
        Log.i("NodeService", "Copy file from " + assetFilePath + " to " + destinationFilePath);

        byte[] buf = new byte[1024];
        int len;
        while ((len = in.read(buf)) > 0)
            out.write(buf, 0, len);
        in.close();
        out.close();
    }

    public static String addTrailingSlash(String path)
    {
        if (path.charAt(path.length() - 1) != '/')
        {
            path += "/";
        }
        return path;
    }

    public static String addLeadingSlash(String path)
    {
        if (path.charAt(0) != '/')
        {
            path = "/" + path;
        }
        return path;
    }

    public static void createDir(File dir) throws IOException
    {
        if (dir.exists())
        {
            if (!dir.isDirectory())
            {
                throw new IOException("Can't create directory, a file is in the way");
            }
        } else
        {
            dir.mkdirs();
            if (!dir.isDirectory())
            {
                throw new IOException("Unable to create directory");
            }
        }
    }

    public static void deleteRecursive(File fileOrDirectory) {
        if (fileOrDirectory.isDirectory())
            for (File child : fileOrDirectory.listFiles())
                deleteRecursive(child);

        fileOrDirectory.delete();
    }
}
