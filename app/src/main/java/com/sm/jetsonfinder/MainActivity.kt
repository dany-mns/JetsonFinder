package com.sm.jetsonfinder

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.speech.RecognizerIntent
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import kotlinx.android.synthetic.main.activity_main.*
import java.util.*

class MainActivity : AppCompatActivity() {


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val buttonStart: Button = findViewById(R.id.btnStart)
        buttonStart.setOnClickListener {
            val intent = Intent(this, StartConnection::class.java)
            startActivity(intent)
        }

        val buttonConfig: Button = findViewById(R.id.btnTcpConfig)
        buttonConfig.setOnClickListener {
            val intent = Intent(this, ConfigTcpIp::class.java)
            startActivity(intent)
        }

        val buttonExit: Button = findViewById(R.id.btnExit)
        buttonExit.setOnClickListener {
            finish()
            System.exit(0)
        }
    }
}
