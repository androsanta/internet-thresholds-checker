package andrew.webcubemanager

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys

const val KEY_USERNAME = "username"
const val KEY_PASSWORD = "password"
const val KEY_MSISDN = "msisdn"

fun getSecureSharedPreferences(context: Context): SharedPreferences {
    return EncryptedSharedPreferences.create(
        "secret_shared_prefs",
        MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC),
        context,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
}

fun Float.format(digits: Int) = "%.${digits}f".format(this)