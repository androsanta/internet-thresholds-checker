package andrew.webcubemanager

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import android.widget.Toast
import java.text.SimpleDateFormat
import java.util.*


const val SET_CONNECTION_ON = "set_connection_on"
const val SET_CONNECTION_OFF = "set_connection_off"
const val GET_READING = "get_reading"

class WcmWidget : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        appWidgetIds.forEach { id ->
            val views = RemoteViews(context.packageName, R.layout.wcm_widget)
            views.apply {
                setOnClickPendingIntent(R.id.connection_on_btn, getPendingIntent(context, SET_CONNECTION_ON))
                setOnClickPendingIntent(R.id.connection_off_btn, getPendingIntent(context, SET_CONNECTION_OFF))
                setOnClickPendingIntent(R.id.refresh_btn, getPendingIntent(context, GET_READING))
            }
            appWidgetManager.updateAppWidget(id, views)
        }
    }

    override fun onReceive(context: Context?, intent: Intent?) {
        if (context != null) {
            when (intent?.action) {
                SET_CONNECTION_ON -> setConnection(context, true)
                SET_CONNECTION_OFF -> setConnection(context, false)
                GET_READING -> getReading(context)
            }
        }
        super.onReceive(context, intent)
    }

    private fun getReading(ctx: Context) {
        val manager = Manager(ctx)
        val views = RemoteViews(ctx.packageName, R.layout.wcm_widget)

        setUiLoadingState(views, true)
        updateWidget(ctx, views)

        manager.getReading({ reading ->
            views.apply {
                val (totalGb, remainingGb, date) = reading
                val (
                    percentage,
                    daysToRenew,
                    _,
                    meanDailyLeftGb,
                    actualDailyLeftGb
                ) = reading.getDetailedStatus()

                // Actual daily left
                val actualDailyLeftText = if (actualDailyLeftGb > 1) {
                    "${actualDailyLeftGb.format(2)} Gb"
                } else {
                    "${(actualDailyLeftGb * 100).format(0)} Mb"
                }
                setTextViewText(R.id.actual_left_day, actualDailyLeftText)

                // Next renew + mean daily left
                val nextRenewText =
                    "$daysToRenew day${if (daysToRenew > 1) "s" else ""} (${meanDailyLeftGb.format(2)} Gb daily)"
                setTextViewText(R.id.next_renew_daily_left, nextRenewText)

                // Remaining Gb
                setTextViewText(R.id.remaining, "${remainingGb.format(2)} / ${totalGb.format(2)} Gb")

                // Percentage
                setTextViewText(R.id.percentage, "${percentage.format(1)}%")

                // Progress Bar
                setProgressBar(R.id.percentage_progress_bar, 100, percentage.toInt(), false)

                // Last updated
                val dateText = SimpleDateFormat("d MMMM HH:mm", Locale.ITALY).format(date)
                setTextViewText(R.id.last_text_value, dateText)
            }
            setUiLoadingState(views, false)
            updateWidget(ctx, views)
        }, { e ->
            Toast.makeText(
                ctx, "Cannot get data! $e",
                Toast.LENGTH_LONG
            ).show()
            setUiLoadingState(views, false)
            updateWidget(ctx, views)
        })
    }

    private fun setConnection(ctx: Context, enabled: Boolean) {
        val manager = Manager(ctx)
        val views = RemoteViews(ctx.packageName, R.layout.wcm_widget)

        setUiLoadingState(views, true)
        updateWidget(ctx, views)

        manager.setConnection(enabled, {
            setUiLoadingState(views, false)
            updateWidget(ctx, views)
        }, { e ->
            Toast.makeText(
                ctx, "Cannot set connection, are you in your local network? $e",
                Toast.LENGTH_LONG
            ).show()
            setUiLoadingState(views, false)
            updateWidget(ctx, views)
        })
    }

    private fun setUiLoadingState(views: RemoteViews, loading: Boolean) {
        val buttons = arrayOf(
            R.id.connection_on_btn,
            R.id.connection_off_btn,
            R.id.refresh_btn
        )

        views.apply {
            // If ui is loading buttons are disabled
            buttons.forEach { res ->
                setBoolean(res, "setEnabled", !loading)
            }
            // While progress bar is in indefinite loading state
            setBoolean(R.id.percentage_progress_bar, "setIndeterminate", loading)
        }
    }

    private fun updateWidget(ctx: Context, views: RemoteViews) {
        val componentName = ComponentName(ctx, WcmWidget::class.java)
        AppWidgetManager.getInstance(ctx).updateAppWidget(componentName, views)
    }

    private fun getPendingIntent(context: Context, act: String): PendingIntent {
        return Intent(context, WcmWidget::class.java)
            .apply {
                action = act
            }.let { intent ->
                PendingIntent.getBroadcast(context, 0, intent, 0)
            }
    }

}

