###############################################
#Provenance check

from artifacts.direct_experience import direct_experience


def provenance(ID, author):
    pass
    # file_name = ID + ".txt"
    # log_path = Logging.LOG_PATH / file_name
    # fo = open(log_path.absolute(), "r+")
    # logfile = fo.read()
    # filesize = len(logfile)
    # fo.seek(0)
    # expresult = 0
    # AUTHOR = author.upper()
    # while fo.tell() < filesize:
    #     timelog_line = fo.readline()
    #     if timelog_line[48:49] == author:
    #         expresult = direct_experience(ID, AUTHOR)
    #         #print(expresult)
    #     expresult = expresult
    # fo.close()
    # return format(expresult, '.2f')

    # file_name = ID + ".txt"
    # log_path = Logging.LOG_PATH / file_name
    # provenance_value = 0
    # with open(log_path.absolute(), "r+") as message_log:
    #     last_message = message_log.readlines()[-1]
    #     if last_message[48:49] == author:
    #         provenance_value = float(directxp(ID, author.upper()))
    # return format(provenance_value, '.2f')
