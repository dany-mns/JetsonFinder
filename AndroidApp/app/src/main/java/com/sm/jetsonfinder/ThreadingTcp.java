package com.sm.jetsonfinder;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.Date;

public class ThreadingTcp {

    private String host;
    private int port;
    private ImageView imageView;
    byte[] buffer;

    public ThreadingTcp(String host, int port) {
        this.host = host;
        this.port = port;
        this.buffer = new byte[144800];
    }


    public void getResource(String message) {
        new Thread(new ConnectThread(message)).start();
        setImageViewWithByteArray(imageView, buffer);
    }

    public void setImage(ImageView iv) {
        this.imageView = iv;
    }

    private static void setImageViewWithByteArray(ImageView view, byte[] data) {
        if(data != null) {
            Bitmap bitmap = BitmapFactory.decodeByteArray(data, 0, data.length);
            view.setImageBitmap(bitmap);
        } else {
            Log.i("myapp", "null buffer");
        }
    }

    private void loadLastImage() {
        try {
            Bitmap myBitmap = BitmapFactory.decodeFile("/storage/emulated/0/Signs/from_jetson.jpg");
            this.imageView.setImageBitmap(myBitmap);
        } catch (Exception exp) {
            Log.d("myapp", exp.getMessage());
        }
    }

    private PrintWriter output;
    private Socket socket = null;

    class ConnectThread implements Runnable {

        private String message;

        public ConnectThread(String message) {
            this.message = message;
        }

        public void run() {
            try {
                socket = new Socket(host, port);
                output = new PrintWriter(socket.getOutputStream());

                output.write(message);
                output.flush();

                SimpleDateFormat simpleDateFormat = new SimpleDateFormat("dd-MM-yyyy-hh-mm-ss");
//                String uid = simpleDateFormat.format(new Date());
//                FileOutputStream fileOutputStream = new FileOutputStream("/storage/emulated/0/Signs/from_jetson" + uid + ".jpg");
                FileOutputStream fileOutputStream = null;
                boolean readImage = false;
                int count;

                InputStream input = socket.getInputStream();
                while ((count = input.read(buffer)) > 0) {
                    if(count > 30) {
                        if(fileOutputStream == null) {
                            fileOutputStream = new FileOutputStream("/storage/emulated/0/Signs/from_jetson.jpg");
                            readImage = true;
                        }
                        fileOutputStream.write(buffer, 0, count);
                    }
                    Log.d("myapp", Integer.toString(count));
                }

                if(readImage) {
                    loadLastImage();
                    readImage = false;
                }


                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

}
