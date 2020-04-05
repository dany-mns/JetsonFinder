package com.sm.jetsonfinder

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText

class ConfigTcpIp : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_config_tcp_ip)

        val btnSubmit: Button = findViewById(R.id.btnSavaConfig)
        btnSubmit.setOnClickListener {
            val intent: Intent = Intent(this, StartConnection::class.java)
            intent.putExtra("host", findViewById<EditText>(R.id.textHost).text.toString())
            intent.putExtra("port", findViewById<EditText>(R.id.textPort).text.toString().toInt())
            startActivity(intent)
        }
    }

}
