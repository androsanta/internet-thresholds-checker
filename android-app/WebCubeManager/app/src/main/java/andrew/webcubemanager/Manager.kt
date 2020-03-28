package andrew.webcubemanager

import android.content.Context
import com.android.volley.*
import com.android.volley.toolbox.HttpHeaderParser
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import java.io.UnsupportedEncodingException
import java.net.CookieHandler
import java.net.CookieManager
import java.nio.charset.Charset
import java.util.*
import kotlin.NoSuchElementException
import kotlin.collections.HashMap

class Manager(context: Context) {
    private var queue = Volley.newRequestQueue(context)
    private val sharedPreferences = getSecureSharedPreferences(context)

    fun setConnection(enabled: Boolean, onSuccess: () -> Unit = {}, onError: (e: Any) -> Unit = { _: Any -> }) {
        val baseUrl = "http://192.168.1.1"
        val connectionPageUrl = "$baseUrl/html/mobileconnection.html"
        val apiConnection = "$baseUrl/api/dialup/connection"

        CookieHandler.setDefault(CookieManager())

        val pageRequest = StringRequest(
            Request.Method.GET,
            connectionPageUrl,
            Response.Listener<String> { pageContent ->
                val token: String?
                try {
                    val matches = Regex("<meta name=\"csrf_token\" content=\"([^&#\$/]+)\"/>")
                        .findAll(pageContent)
                    token = matches.last().groupValues[1]
                } catch (e: NoSuchElementException) {
                    return@Listener
                }

                val connectionMode = if (enabled) 0 else 1
                val xmlReq = "<?xml version='1.0' encoding='UTF-8'?><request>" +
                        "<RoamAutoConnectEnable>0</RoamAutoConnectEnable><MaxIdelTime>600</MaxIdelTime>" +
                        "<ConnectMode>$connectionMode</ConnectMode><MTU>1440</MTU>" +
                        "<auto_dial_switch>1</auto_dial_switch>" +
                        "<pdp_always_on>0</pdp_always_on></request>"

                val apiRequest = object : StringRequest(
                    Method.POST,
                    apiConnection,
                    Response.Listener<String> { onSuccess() },
                    Response.ErrorListener { e ->
                        onError(e)
                    }
                ) {
                    @Throws(AuthFailureError::class)
                    override fun getHeaders(): Map<String, String> {
                        return HashMap<String, String>().apply {
                            put("__RequestVerificationToken", token)
                            put("Referer", connectionPageUrl)
                        }
                    }

                    override fun getBody(): ByteArray = xmlReq.toByteArray()
                    override fun getBodyContentType(): String = "application/xml"
                }

                queue.add(apiRequest)
            },
            Response.ErrorListener { e ->
                onError(e)
            }
        )
        queue.add(pageRequest)
    }

    fun getReading(onSuccess: (Reading) -> Unit = { _: Reading -> }, onError: (e: Any) -> Unit = { _: Any -> }) {
        val api = "https://apigw.windtre.it"
        val apiLogin = "$api/api/v1/login/credentials"
        val apiThreshold = "$api/piksel/api/offerService/getThreshold"

        val username = sharedPreferences.getString(KEY_USERNAME, null)
        val password = sharedPreferences.getString(KEY_PASSWORD, null)
        val msisdn = sharedPreferences.getString(KEY_MSISDN, null)

        if (username == null || password == null || msisdn == null) {
            onError("Please set credentials first!")
            return
        }

        val credentials = Credentials(username, password)

        val headers = HashMap<String, String>().apply {
            put("X-Brand", "ONEBRAND")
            put("X-Wind-Client", "Web")
        }

        val loginReq = GsonRequest(
            Request.Method.POST,
            apiLogin,
            LoginResponse::class.java,
            { response ->
                if (response.headers != null) {
                    val token = response.headers["X-W3-Token"]

                    val authHead = HashMap<String, String>().apply {
                        put("X-Wind-Client", "Web")
                        put("Authorization", "Bearer $token")
                    }

                    val thresholdReq = GsonRequest(
                        Request.Method.POST,
                        apiThreshold,
                        ThresholdResponse::class.java,
                        { thresholdRes ->
                            val data = thresholdRes.data
                            if (data.success) {
                                val offer = data.response["threshold"]
                                    .asJsonArray[0]
                                    .asJsonObject["detailList"]
                                    .asJsonObject["offer"]
                                    .asJsonArray[0]
                                    .asJsonObject
                                val initialAmount = offer["initialAmount"].asFloat
                                val usedAmount = offer["usedAmount"].asFloat
                                onSuccess(
                                    Reading(
                                        initialAmount / 1000,
                                        (initialAmount - usedAmount) / 1000,
                                        Date()
                                    )
                                )
                            } else {
                                onError("Cannot get threshold!")
                            }
                        },
                        onError,
                        ThresholdRequest(msisdn),
                        authHead
                    )

                    queue.add(thresholdReq)
                } else {
                    onError("Cannot get login token!")
                }
            },
            onError,
            credentials,
            headers
        )

        queue.add(loginReq)
    }
}


class GsonRequest<T>(
    method: Int,
    url: String,
    private val clazz: Class<T>,
    private val onSuccess: (Res<T>) -> Unit,
    private val onError: (e: Any) -> Unit,
    private val data: Any? = null,
    private val headers: MutableMap<String, String>? = null
) : Request<GsonRequest.Res<T>>(method, url, Response.ErrorListener { e -> onError(e) }) {

    private val gson = Gson()

    data class Res<T>(
        val data: T,
        val headers: MutableMap<String, String>?
    )

    override fun getHeaders(): MutableMap<String, String> = headers ?: super.getHeaders()

    override fun getBody(): ByteArray {
        return if (data != null) {
            gson.toJson(data).toByteArray()
        } else {
            super.getBody()
        }
    }

    override fun getBodyContentType(): String {
        return if (data != null) {
            "application/json"
        } else {
            super.getBodyContentType()
        }
    }

    override fun parseNetworkResponse(response: NetworkResponse?): Response<Res<T>> {
        return try {
            val json = String(
                response?.data ?: ByteArray(0),
                Charset.forName(HttpHeaderParser.parseCharset(response?.headers))
            )
            Response.success(
                Res(gson.fromJson(json, clazz), response?.headers),
                HttpHeaderParser.parseCacheHeaders(response)
            )
        } catch (e: UnsupportedEncodingException) {
            Response.error(ParseError(e))
        } catch (e: JsonSyntaxException) {
            Response.error(ParseError(e))
        }
    }

    override fun deliverResponse(response: Res<T>?) = onSuccess(response!!)

}
