package com.sm.jetsonfinder;

import android.content.Context;
import android.os.Environment;
import android.util.Log;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;

public class ThreadingTcp {

    private String host;
    private int port;
    Thread Thread1 = null;

    public ThreadingTcp(String host, int port) {
        this.host = host;
        this.port = port;
    }

    public void sendMessage(String message) {
        new Thread(new Thread3(message)).start();
    }

    public void receiveMessage() {
        Thread1 = new Thread(new Thread1());
        Thread1.start();
    }

    private PrintWriter output;
    private InputStream input;
    private Socket socket = null;

    class Thread1 implements Runnable {
        public void run() {
            try {
                socket = new Socket(host, port);
                output = new PrintWriter(socket.getOutputStream());
                new Thread(new Thread2()).start();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    class Thread2 implements Runnable {
        @Override
        public void run() {
            try {
                InputStream input = socket.getInputStream();
                FileOutputStream fileOutputStream = new FileOutputStream("/storage/emulated/0/Signs/jetson.jpg");
                byte[] buffer = new byte[12288];
                int count;
                while ((count = input.read(buffer)) > 0) {
                    fileOutputStream.write(buffer, 0, count);
                }
            }catch (IOException e) {
                e.printStackTrace();
            }
        }
    }


    class Thread3 implements Runnable {
        private String message;
        Thread3(String message) {
            this.message = message;
        }
        @Override
        public void run() {
            output.write(message);
            output.flush();
            Log.i("ThJetson", "Catre server: " + message);
        }
    }
}
