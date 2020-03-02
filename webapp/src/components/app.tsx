import React from 'react'
import {Box, Container, Icon, Paper, Typography} from '@material-ui/core'
import {ThemeProvider} from '@material-ui/core/styles'
import {theme} from '../theme'
import './app.css'
import {WebCubeStatus} from './web-cube-status'

export const App: React.FC = () => {
    return (
        <ThemeProvider theme={theme}>
            <Container fixed maxWidth='md' className='no-pad'>
                <Paper className='toolbar'>
                    <Box display='flex' flexDirection='row' alignItems='center' className='title'>
                        <Typography color='textPrimary' variant='h4'>Web</Typography>
                        <Typography color='textSecondary' variant='h4'>Cube</Typography>
                        <Icon>bar_chart</Icon>
                    </Box>
                </Paper>
                <WebCubeStatus/>
            </Container>
        </ThemeProvider>
    )
}