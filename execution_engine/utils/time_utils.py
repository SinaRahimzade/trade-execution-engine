import datetime


def time_floor(dt, t):
    return dt - datetime.timedelta(
        minutes=dt.minute % t, seconds=dt.second, microseconds=dt.microsecond
    )


def time_ceil(dt, t):
    return time_floor(dt, t) + datetime.timedelta(minutes=t)
