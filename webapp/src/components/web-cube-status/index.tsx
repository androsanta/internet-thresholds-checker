import React, {useEffect, useState} from 'react'
import './style.css'
import {Box, Fab, Icon, LinearProgress, Paper, Snackbar, Typography} from '@material-ui/core'
import moment from 'moment'


interface Reading {
    date: string
    percentage: number
    remainingGb: number
    totalGb: number
    actualDailyLeftGb: number
    daysToRenew: number
    meanDailyLeftGb: number
}

interface Status {
    connected: boolean
    reading: Reading
    trafficExceeded: boolean
}

interface props {
    status: Status
}

const WebCubeStatusContent: React.FC<props> = ({status}) => {
    const {connected, reading, trafficExceeded} = status
    const {date, percentage, remainingGb, totalGb, actualDailyLeftGb, daysToRenew, meanDailyLeftGb} = reading

    const nextRenewMsg = `Next renew in ${daysToRenew} day${daysToRenew > 1 ? 's' : ''} (${meanDailyLeftGb.toFixed(2)} Gb daily)`

    const initMsg = actualDailyLeftGb >= 0 ? 'You have' : 'You are down'
    const mainMessage = `${initMsg} ${actualDailyLeftGb.toFixed(2)} Gb for today`

    return (
        <>
            <Box display='flex' flexDirection='row' alignItems='center' justifyContent='flex-end'>
                <Typography>{connected ? 'Connected' : 'Not connected'}</Typography>
                <div className={`circle ${connected ? 'green' : 'red'}`}/>
            </Box>
            <Typography variant='h5'>{mainMessage}</Typography>
            <Typography>{nextRenewMsg}</Typography>
            <Typography>Remaining: {remainingGb.toFixed(2)} / {totalGb.toFixed(2)} Gb</Typography>
            <Box display='flex' flexDirection='row' alignItems='center' justifyContent='center'>
                <Typography>{(+percentage).toFixed(2)}%</Typography>
                <LinearProgress variant='determinate' value={percentage}
                                style={{height: '10px', width: '80%', borderRadius: '5px', marginLeft: '10px'}}/>
            </Box>
            <Typography style={{fontSize: '10pt', marginBottom: '10px'}}>Last
                Update: {moment(date).format('H:m - dddd, MMM Do')}</Typography>
        </>
    )
}

export const WebCubeStatus: React.FC = () => {
    const [status, setStatus] = useState(null)
    const [open, setOpen] = useState(false)

    const getStatus = () => {
        fetch(`api/status`)
            .then(res => res.json())
            .then(setStatus)
            .catch(() => setOpen(true))
    }

    useEffect(getStatus, [])
    // @ts-ignore
    const content = status !== null && <WebCubeStatusContent status={status}/>
    return (
        <Paper className='background'>
            <div className='content'>
                {content}
            </div>
            <Fab className='refresh-fab' onClick={getStatus}>
                <Icon>refresh</Icon>
            </Fab>
            <Snackbar open={open} autoHideDuration={5000} onClose={() => setOpen(false)}
                      message='Error getting status'/>
        </Paper>
    )
}