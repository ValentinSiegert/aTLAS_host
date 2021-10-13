from datetime import *

###############################################################
# Age checking


def age_check(ID, entity, tag):
    pass
    # file_name = ID + ".txt"
    # log_path = Logging.LOG_PATH / file_name
    # fo = open(log_path.absolute(), "r+")
    # logfile = fo.read()
    # filesize = len(logfile)
    # fo.seek(0)
    # r_count = 0
    # today = datetime.now()
    # today = today.date()
    # intime = 0
    # outdated = 0
    #
    # #After opening the logfile, line for line is parsed to look if the searched
    # #tag is outdated or not. If so, a negative value is returned
    #
    # while fo.tell() < filesize:
    #     timelog_line = fo.readline()
    #     if timelog_line[37:38] == entity:
    #         tr = datetime.strptime(timelog_line[0:10], "%Y-%m-%d").date()
    #
    #         gap = today - timedelta(days=10)
    #
    #         if tr < gap and timelog_line[56:58] == tag:
    #             r_count = r_count + 1
    #             intime = intime + 0.1
    #
    #         else:
    #             outdated = outdated - 0.1
    # fo.close()
    # if intime > 1:
    #     intime = 1
    # if outdated < -1:
    #     outdated = -1
    # return intime + outdated

