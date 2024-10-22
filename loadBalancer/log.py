import sys

from datetime import datetime


def logit(fileObj, msg):
    fileObj.write("[ %s ] %s" %(datetime.now().ctime(), msg))
    if msg[-1] != '\n':
        fileObj.write('\n')
    fileObj.flush()


def logmsg(msg):
    logit(sys.stdout, msg)


def logerr(msg):
    logit(sys.stderr, msg)
