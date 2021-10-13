
def recency(ID, tag):
    pass
    # file_name = ID + ".txt"
    # log_path = Logging.LOG_PATH / file_name
    # fo = open(log_path.absolute(), "r+")
    # logfile = fo.read()
    # filesize = len(logfile)
    # fo.seek(0)
    # result_count = 0
    # ex = 0
    # result = 0
    # while fo.tell() < filesize:
    #     timelog_line = fo.readline()
    #     if timelog_line[56:58] == tag:
    #         service_satisfaction = timelog_line[59:63]
    #         if timelog_line[59:63] == '0 |m':
    #             service_satisfaction = timelog_line[59:60]
    #         result_count = result_count + 1
    #         ex += float(service_satisfaction)
    #         if result_count == 10:
    #             break
    #         result = format(ex / result_count, '.2f')
    # return result

