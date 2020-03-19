export interface DetailedStatus {
    percentage: number
    daysToRenew: number
    actualRemainingGb: number
    meanDailyLeftGb: number
    actualDailyLeftGb: number
}

export interface Reading {
    totalGb: number
    remainingGb: number
    date: string
}

export interface Status {
    reading: Reading
    connected: boolean
    trafficExceeded: boolean
}

export interface StatusResponse {
    status: Status
    details: DetailedStatus
}