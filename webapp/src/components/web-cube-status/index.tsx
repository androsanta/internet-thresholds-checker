import React, {useEffect, useState} from 'react'
import './style.css'
import {Box, CircularProgress, Fab, Icon, LinearProgress, Paper, Typography} from '@material-ui/core'
import moment from 'moment'
import {DetailedStatus, Status, StatusResponse} from '../../models'

interface props {
    status: Status
    details: DetailedStatus
}

const WebCubeStatusContent: React.FC<props> = ({status, details}) => {
    const {connected, reading, trafficExceeded} = status
    const {date, remainingGb, totalGb} = reading
    const {percentage, daysToRenew, meanDailyLeftGb, actualDailyLeftGb} = details

    const nextRenewMsg = `Next renew in ${daysToRenew} day${daysToRenew > 1 ? 's' : ''} (${meanDailyLeftGb.toFixed(2)} Gb daily)`

    const initMsg = actualDailyLeftGb >= 0 ? 'You have' : 'You are down'
    const mainMessage = `${initMsg} ${actualDailyLeftGb.toFixed(2)} Gb for today`

    return (
        <>
            <Box display='flex' flexDirection='row' alignItems='center' justifyContent='flex-end'>
                <Typography>{connected ? 'Connected' : 'Not connected'}</Typography>
                <div className={`circle ${connected ? 'green' : 'red'}`}/>
            </Box>
            <Typography variant='h5' style={trafficExceeded ? {color: 'red'} : {}}>{mainMessage}</Typography>
            <Typography>{nextRenewMsg}</Typography>
            <Typography>Remaining: {remainingGb.toFixed(2)} / {totalGb.toFixed(2)} Gb</Typography>
            <Box display='flex' flexDirection='row' alignItems='center' justifyContent='center'>
                <Typography>{percentage.toFixed(2)}%</Typography>
                <LinearProgress variant='determinate' value={percentage}
                                style={{height: '10px', width: '80%', borderRadius: '5px', marginLeft: '10px'}}/>
            </Box>
            <Typography style={{fontSize: '10pt', marginBottom: '10px'}}>Last
                Update: {moment(date).format('H:m - dddd, MMM Do')}</Typography>
        </>
    )
}

export const WebCubeStatus: React.FC = () => {
    const [statusResponse, setStatusResponse] = useState<StatusResponse | undefined>()
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [errorMsg, setErrorMsg] = useState<string | undefined>()

    const getStatus = () => {
        console.log('fetching data')
        setIsLoading(true)
        fetch(`api/status`)
            .then(res => res.json())
            .then(res => {
                console.log('data', res)
                setStatusResponse(res)
                setErrorMsg(undefined)
            })
            .catch(setErrorMsg)
            .finally(() => setIsLoading(false))
    }

    useEffect(getStatus, [])
    // @ts-ignore
    const content = statusResponse &&
        <WebCubeStatusContent status={statusResponse.status} details={statusResponse.details}/>
    return (
        <Paper className='background'>
            <div className='content'>
                {content}
                {isLoading && <div className='loader'>
                    <CircularProgress/>
                </div>}
                {errorMsg && <div className='loader'>
                    <Typography>{errorMsg.toString()}</Typography>
                </div>}
            </div>
            <Fab disabled={isLoading} className='refresh-fab' onClick={getStatus}>
                <Icon>refresh</Icon>
            </Fab>
        </Paper>
    )
}