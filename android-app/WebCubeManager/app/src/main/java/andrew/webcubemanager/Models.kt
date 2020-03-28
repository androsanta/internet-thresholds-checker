package andrew.webcubemanager

import com.google.gson.JsonObject
import com.google.gson.annotations.SerializedName
import java.util.*

const val threshold = 5
const val dailyThreshold = 0.9f

data class Reading(
    @SerializedName("totalGb") val totalGb: Float,
    @SerializedName("remainingGb") val remainingGb: Float,
    @SerializedName("date") val date: Date
) {
    fun getDetailedStatus(): DetailedStatus {
        val c = Calendar.getInstance().apply { time = date }
        val daysToRenew = 7 - ((c.get(Calendar.DAY_OF_WEEK) - 1) % 7)
        val actualRemainingGb = remainingGb - (totalGb / 100) * threshold
        val meanDailyLeftGb = if (daysToRenew > 1) {
            actualRemainingGb / (daysToRenew - 1)
        } else {
            actualRemainingGb
        }

        return DetailedStatus(
            (remainingGb / totalGb) * 100,
            daysToRenew,
            actualRemainingGb,
            meanDailyLeftGb,
            actualRemainingGb - (dailyThreshold * (daysToRenew - 1))
        )
    }
}

data class DetailedStatus(
    val percentage: Float,
    val daysToRenew: Int,
    val actualRemainingGb: Float,
    val meanDailyLeftGb: Float,
    val actualDailyLeftGb: Float
)

data class Credentials(
    @SerializedName("username") val username: String,
    @SerializedName("password") val password: String
)

data class ThresholdRequest(
    @SerializedName("msisdn") val msisdn: String
)

data class LoginResponse(
    @SerializedName("status") val status: String
)

data class ThresholdResponse(
    @SerializedName("success") val success: Boolean,
    @SerializedName("response") val response: JsonObject
)
