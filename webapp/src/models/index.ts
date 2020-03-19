export interface DetailedStatus {
    percentage: number
    days_to_renew: number
    actual_remaining_gb: number
    mean_daily_left_gb: number
    actual_daily_left_gb: number
}

export interface Reading {
    total_gb: number
    remaining_gb: number
    date: string
}

export interface Status {
    reading: Reading
    connected: boolean
    traffic_exceeded: boolean
}

export interface StatusResponse {
    status: Status
    details: DetailedStatus
}