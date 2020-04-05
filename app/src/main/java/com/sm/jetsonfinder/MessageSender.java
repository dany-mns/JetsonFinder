package com.sm.jetsonfinder;

import android.os.AsyncTask;
import android.os.Handler;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class MessageSender extends AsyncTask<String, Void, Void> {

    Socket s;
    TextView tv;
    DataOutputStream dos;
    PrintWriter pw;

    public MessageSender (TextView tv){
        this.tv = tv;

    }

    @Override
    protected Void doInBackground(String... voids) {

        String message = voids[0];

        try {
            s = new Socket("192.168.1.5", 1998);
//            This part write text to server

            pw = new PrintWriter(s.getOutputStream());
            pw.write(message);
            pw.flush();
            pw.close();

//            This part receive text from server but not concurently with write
//            try {
//                InputStreamReader isr = new InputStreamReader(s.getInputStream());
//                BufferedReader br = new BufferedReader(isr);
//                String messages = br.readLine();
//                if(!messages.equals("")){
//                    tv.setText(messages);
//                } else {
//                    tv.setText("Fail");
//                }
//
//            } catch (Exception e) {
//                e.printStackTrace();
//            }
            s.close();


        } catch (IOException e) {
            e.printStackTrace();
        }

        return null;
    }
}
