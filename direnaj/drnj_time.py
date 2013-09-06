# This file defines the functions for time conversion
#

import time

number_of_days_from_1_Jan_0000_to_1_Jan_1970 = 719529.0;

def now_in_drnj_time():
    t = time.time()
    return py_time2drnj_time(t)

def drnj_time2py_time(dt):
	"""
	 dt : days from 1-Jan-0000
	 returns seconds from 1 Jan  1970
	"""
	t = (dt-number_of_days_from_1_Jan_0000_to_1_Jan_1970)*24.0*60*60;
	return t

def py_time2drnj_time(t):
	"""
	 t : seconds from 1-Jan-1970
	 returns days from 1 Jan 0000
	"""
	dt = number_of_days_from_1_Jan_0000_to_1_Jan_1970 + t/(24.0*60*60);
	return dt

def py_utc_time2drnj_time(time_str):
    """

    """
    utc_time_format = '%a %b %d %H:%M:%S +0000 %Y'
    t = time.strptime(time_str, utc_time_format)
    import calendar
    t = calendar.timegm(t)
    return py_time2drnj_time(t)
