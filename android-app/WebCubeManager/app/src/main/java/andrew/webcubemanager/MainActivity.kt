package andrew.webcubemanager

import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.addTextChangedListener
import com.afollestad.materialdialogs.MaterialDialog
import com.afollestad.materialdialogs.WhichButton
import com.afollestad.materialdialogs.actions.setActionButtonEnabled
import com.afollestad.materialdialogs.bottomsheets.BottomSheet
import com.afollestad.materialdialogs.customview.customView
import com.afollestad.materialdialogs.customview.getCustomView
import com.google.android.material.textview.MaterialTextView
import kotlinx.android.synthetic.main.activity_main.*


class MainActivity : AppCompatActivity() {
    private lateinit var sharedPreferences: SharedPreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sharedPreferences = getSecureSharedPreferences(this)

        val usernameTv = findViewById<MaterialTextView>(R.id.username)
        usernameTv.apply {
            text = sharedPreferences.getString(KEY_USERNAME, "Not set yet!")
        }

        change_account_btn.setOnClickListener {
            var username: String? = null
            var password: String? = null
            var msisdn: String? = null

            val dialog = MaterialDialog(this, BottomSheet()).show {
                title(R.string.set_your_account)
                message(R.string.account_set_message)
                customView(R.layout.bottom_sheet_content, horizontalPadding = true)
                positiveButton(R.string.set) {
                    if (username != null && password != null && msisdn != null) {
                        sharedPreferences.edit()
                            .putString(KEY_USERNAME, username)
                            .putString(KEY_PASSWORD, password)
                            .putString(KEY_MSISDN, msisdn)
                            .apply()
                        usernameTv.text = username
                    } else {
                        Toast.makeText(this@MainActivity, R.string.fill_fields, Toast.LENGTH_SHORT).show()
                    }
                }
                negativeButton(R.string.cancel)
                setActionButtonEnabled(WhichButton.POSITIVE, false)
            }

            fun checkInput() {
                if (username != null && password != null) {
                    dialog.setActionButtonEnabled(WhichButton.POSITIVE, true)
                } else {
                    dialog.setActionButtonEnabled(WhichButton.POSITIVE, false)
                }
            }

            dialog.getCustomView().apply {
                findViewById<EditText>(R.id.username)
                    .addTextChangedListener { text ->
                        username = text.toString()
                        checkInput()
                    }
                findViewById<EditText>(R.id.password)
                    .addTextChangedListener { text ->
                        password = text.toString()
                        checkInput()
                    }
                findViewById<EditText>(R.id.msisdn)
                    .addTextChangedListener { text ->
                        msisdn = text.toString()
                        checkInput()
                    }
            }
        }
    }

}
