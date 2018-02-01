__all__ = ['StopWatch']

import re
import time
import csv
from io import StringIO

from collections import OrderedDict, defaultdict




class StopWatch:
    __START_PROBE_TAG = 'start'
    __STOP_PROBE_TAG = 'stop'
    __DEFAULT_CLICK_TAG_FORMAT = 'click-{:d}'
    __CUSTOM_TAG_FORMAT = re.compile(r'{{(.*?)}}')
    __CUSTOM_TAG_QUICK_REPLACE = lambda tag: '{{'+str(tag)+'}}'

    __CSV_TAG_HEADLINE = 'Tag'
    __CSV_ELAPSED_TIME_HEADLINE = 'Elapsed Time'

    def __init__(self, debug=False, autostart=False, custom_tags=True):
        self.probes = OrderedDict()
        self.probes_n = 0
        self.debug_mode = debug
        self.custom_tags = defaultdict(lambda: 0)
        self.custom_tags_enabled = custom_tags
        if autostart:
            self.start()

    def start(self):
        """
        Starts the stopwatch
        :return:
        """
        self.probes[StopWatch.__START_PROBE_TAG] = time.time()

    def stop(self):
        """
        Stops the stopwatch
        :return:
        """
        self.probes[StopWatch.__STOP_PROBE_TAG] = time.time()

    def click(self, tag=None):
        """
        Stores elapsed time from the start of the stopwatch time untill this moment.
        If StopWatch wasn't already running it starts it.
        :param tag: Probe's tag. If not present it will choose 'default'
        :return:
        """
        aux = time.time()

        if not tag:
            tag = StopWatch.__DEFAULT_CLICK_TAG_FORMAT.format(self.probes_n)
            self.probes_n += 1

        if StopWatch.__START_PROBE_TAG not in self.probes:
            self.probes[StopWatch.__START_PROBE_TAG] = aux

        if self.custom_tags_enabled:
            tag = self.__populate_custom_tag(tag)

        self.probes[tag] = aux - self.probes[StopWatch.__START_PROBE_TAG]

        return self.probes[tag]

    def pprint_probes(self):
        """
        Pretty prints all probes registered up to now.
        :return:
        """

        print("TAG\t\t\t ELAPSED TIME")
        print("---\t\t\t ------------\n")
        for tag, elapsed_time in self.probes.items():
            print(tag + "\t\t", elapsed_time)

    def csv_dump(self, filepath=""):
        """
        Dumps all probe information to a csv file
        :param filepath: Path to the taget file
        :return:
        """
        with open(filepath, 'w', newline='') as csvfile:
            self.__write_csv(csvfile)

    def csv_dumps(self):
        """
        Dumps all probe information into a csv formatted string
        :return: String with csv encoded information about the probes
        """
        result = self.__write_csv(StringIO())
        return result.getvalue()

    def __write_csv(self, file):
        """
        Writes all probe information to a generic file
        :param file: Input file
        :return: File used to write all information
        """
        fieldnames = [StopWatch.__CSV_TAG_HEADLINE, StopWatch.__CSV_ELAPSED_TIME_HEADLINE]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for tag, elapsed_time in self.probes.items():
            writer.writerow({StopWatch.__CSV_TAG_HEADLINE: tag, StopWatch.__CSV_ELAPSED_TIME_HEADLINE: elapsed_time})
        return file

    def __populate_custom_tag(self, tag):
        found_tags = StopWatch.__CUSTOM_TAG_FORMAT.findall(tag)
        if not found_tags:
            return tag
        for found_tag in found_tags:
            tag = tag.replace(StopWatch.__CUSTOM_TAG_QUICK_REPLACE(found_tag), str(self.custom_tags[found_tag]))
            self.custom_tags[found_tag] += 1
        return tag

    @property
    def elapsed_time(self):
        """
        Elapsed time from starting time to finished time. If the stopwatch is still running it takes now as the finished time.
        :return: Elapsed time
        """
        aux = time.time()
        return self.probes.get(StopWatch.__STOP_PROBE_TAG, aux) - self.probes.get(StopWatch.__START_PROBE_TAG, aux)
