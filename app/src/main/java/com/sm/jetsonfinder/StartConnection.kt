package com.sm.jetsonfinder

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.speech.RecognizerIntent
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.io.BufferedReader
import java.io.IOException
import java.io.PrintWriter
import java.net.Socket
import java.util.*

class StartConnection : AppCompatActivity() {

    val output: PrintWriter? = null
    private val input: BufferedReader? = null

    private val REQUEST_CODE_SPEECH_INPUT = 100
    private lateinit var txtView: TextView
    private var HOST = "192.168.1.5"
    private var PORT = 1998
    private val th: ThreadingTcp = ThreadingTcp(HOST, PORT)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_start_connection)

//        If user come from ConfigTcpIp
        val extras = intent.extras
        if(extras != null) {
            HOST = extras.getString("host").toString()
            PORT = extras.getInt("port")
        }


        txtView = findViewById(R.id.txtReceive)
        th.receiveMessage()
        val btnSpeech: Button = findViewById(R.id.btnSpeech)
        btnSpeech.setOnClickListener {
            speak()
        }

    }



    private fun speak() {
        try{
            val mIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            mIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            mIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            mIntent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Da-mi comenzi in engleza:")
            startActivityForResult(mIntent, REQUEST_CODE_SPEECH_INPUT)
        } catch (e: Exception) {
            Toast.makeText(this, e.message, Toast.LENGTH_SHORT).show()
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        when(requestCode) {
            REQUEST_CODE_SPEECH_INPUT -> {
                if(resultCode == Activity.RESULT_OK && null != data) {
                    val result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                    val txtSpeech: TextView = findViewById(R.id.txtSpeech)
                    txtSpeech.text = result[0]
                    th.sendMessage(result[0])
                }
            }
        }
    }
}
