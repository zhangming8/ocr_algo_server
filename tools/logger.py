import logging
from logging.handlers import TimedRotatingFileHandler
import os
import time
import multiprocessing

lock = multiprocessing.Lock()
logger_dict = {}


class SafeRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)

    """
    Override doRollover
    lines commanded by "##" is changed by cc
    """

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        Override,   1. if dfn not exist then do rename
                    2. _open with "a" models
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        with lock:
            if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
            if self.backupCount > 0:
                for s in self.getFilesToDelete():
                    os.remove(s)
        if not self.delay:
            self.mode = "a"
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


def get_logger(log_file):
    if log_file in logger_dict.keys():
        return logger_dict[log_file]
    # create log file
    if not os.path.exists(os.path.dirname(log_file)):
        os.mkdir(os.path.dirname(log_file))
    if not os.path.exists(log_file):
        open(log_file, "a+").close()
    # logger
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.INFO)
    # fhandler
    handler = logging.handlers.TimedRotatingFileHandler(filename=log_file, when='D', interval=1, backupCount=7)

    # handler = SafeRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=30, encoding='utf-8')
    strfmt = "[%(asctime)s] %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
    # format
    formatter = logging.Formatter(strfmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger_dict[log_file] = logger
    return logger
