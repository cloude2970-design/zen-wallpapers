package com.cloude.zenwallpapers;

import android.app.WallpaperManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Handler;
import android.os.Looper;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@CapacitorPlugin(name = "WallpaperPlugin")
public class WallpaperPlugin extends Plugin {

    private ExecutorService executor = Executors.newSingleThreadExecutor();
    private Handler mainHandler = new Handler(Looper.getMainLooper());

    @PluginMethod
    public void setWallpaper(PluginCall call) {
        String imageUrl = call.getString("url");
        
        if (imageUrl == null || imageUrl.isEmpty()) {
            call.reject("No URL provided");
            return;
        }

        executor.execute(() -> {
            try {
                // Download image
                URL url = new URL(imageUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setDoInput(true);
                connection.connect();
                InputStream input = connection.getInputStream();
                Bitmap bitmap = BitmapFactory.decodeStream(input);
                input.close();

                if (bitmap == null) {
                    mainHandler.post(() -> call.reject("Failed to decode image"));
                    return;
                }

                // Set as wallpaper
                WallpaperManager wallpaperManager = WallpaperManager.getInstance(getContext());
                wallpaperManager.setBitmap(bitmap);
                
                bitmap.recycle();

                mainHandler.post(() -> {
                    JSObject result = new JSObject();
                    result.put("success", true);
                    call.resolve(result);
                });

            } catch (Exception e) {
                mainHandler.post(() -> call.reject("Failed to set wallpaper: " + e.getMessage()));
            }
        });
    }

    @PluginMethod
    public void setWallpaperWithTarget(PluginCall call) {
        String imageUrl = call.getString("url");
        String target = call.getString("target", "both"); // home, lock, both
        
        if (imageUrl == null || imageUrl.isEmpty()) {
            call.reject("No URL provided");
            return;
        }

        executor.execute(() -> {
            try {
                URL url = new URL(imageUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setDoInput(true);
                connection.connect();
                InputStream input = connection.getInputStream();
                Bitmap bitmap = BitmapFactory.decodeStream(input);
                input.close();

                if (bitmap == null) {
                    mainHandler.post(() -> call.reject("Failed to decode image"));
                    return;
                }

                WallpaperManager wallpaperManager = WallpaperManager.getInstance(getContext());
                
                int flag = WallpaperManager.FLAG_SYSTEM | WallpaperManager.FLAG_LOCK;
                if (target.equals("home")) {
                    flag = WallpaperManager.FLAG_SYSTEM;
                } else if (target.equals("lock")) {
                    flag = WallpaperManager.FLAG_LOCK;
                }
                
                wallpaperManager.setBitmap(bitmap, null, true, flag);
                bitmap.recycle();

                mainHandler.post(() -> {
                    JSObject result = new JSObject();
                    result.put("success", true);
                    call.resolve(result);
                });

            } catch (Exception e) {
                mainHandler.post(() -> call.reject("Failed to set wallpaper: " + e.getMessage()));
            }
        });
    }
}
