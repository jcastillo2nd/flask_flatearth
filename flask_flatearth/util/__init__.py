import datetime
import time
from email import utils


def rfc2822_now():
    return utils.formatdate(time.mktime(datetime.datetime.now().timetuple()))
