# -*- coding:utf-8 -*-

import datetime
import csv
import json
import time
import logging
from config import (CSV_FIELD_NAMES, FILTER_PATH, YEST_SESSION_PATH,
                    BASE_PATH, PLATFORM, FILTER_PATH, FILTER_INFO_DIR)
import os

'''
    function: filter user data and save to csv.
'''


class FilterInfo(object):
    def __init__(self):
        self.data_type = "Session"
        self.platform = int(os.getenv("PLATFORM"))

        self.begin_day_id = (datetime.datetime.now()
                             - datetime.timedelta(days=1)).strftime("%Y%m%d")
        self.platform_content = PLATFORM[self.platform]

    def read_session(self, zg_id):
        yest_session_path = YEST_SESSION_PATH.format(platform=self.platform_content,
                                                     begin_day_id=self.begin_day_id)
        with open(yest_session_path,
                  'r') as f:
            for read_line in f:
                line_dic = json.loads(read_line)
                if line_dic["zg_id"] == zg_id:
                    yield line_dic

    def read_user_base(self):
        info_path = BASE_PATH.format(self.platform_content)
        with open(info_path, 'r') as f:
            for read_line in f:
                line_dic = json.loads(read_line)

                yield (line_dic["zg_id"],
                       line_dic["app_user_id"])

    def init_write_csv(self):

        if not os.path.exists(FILTER_INFO_DIR):
            os.makedirs(FILTER_INFO_DIR)
        filter_path = FILTER_PATH.format(platform=self.platform_content,
                                         begin_day_id=self.begin_day_id)

        with open(filter_path, 'a') as csv_file:

            writer = csv.DictWriter(csv_file, CSV_FIELD_NAMES)

            field_dict = {key: key for key in CSV_FIELD_NAMES}
            writer.writerow(field_dict)

    def write_csv(self, user_id, events):
        filter_path = FILTER_PATH.format(platform=self.platform_content,
                                         begin_day_id=self.begin_day_id)
        with open(filter_path, 'a') as csv_file:

            writer = csv.DictWriter(csv_file, CSV_FIELD_NAMES)
            for event in events:
                time_array = time.localtime(event["beginDate"]/1000)
                str_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)

                writer.writerow({CSV_FIELD_NAMES[0]: int(user_id),
                                 CSV_FIELD_NAMES[1]: str_style_time,
                                 CSV_FIELD_NAMES[2]: event["eventName"],
                                 CSV_FIELD_NAMES[3]: event["ip"],
                                 CSV_FIELD_NAMES[4]: (5 if self.platform == 3
                                                  else self.platform),
                                 CSV_FIELD_NAMES[5]: str(event["column_code"])})

    def write_filter_info(self):
        for search_zg_id, search_user_id in self.read_user_base():
            # filter user.
            if search_user_id is not None:
                for line in self.read_session(search_zg_id):
                    # filter events.
                    if len(line["events"]) is 0:
                        continue
                    # write user events data.
                    try:
                        user_id_int = int(search_user_id)
                    except ValueError:
                        logging.warning("user_id:{}".format(search_user_id))
                        continue

                    self.write_csv(user_id=search_user_id,
                                   events=line["events"])

if __name__ == "__main__":

    filter_info = FilterInfo()
    filter_info.init_write_csv()
    filter_info.write_filter_info()
