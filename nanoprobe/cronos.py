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
    __CUSTOM_AUTOINCREMENT_TAG_FORMAT = re.compile(r'{{(.*?)}}')
    __CUSTOM_AUTOINCREMENT_TAG_QUICK_REPLACE = lambda tag: '{{' + str(tag) + '}}'
    __CUSTOM_NONINCREMENTAL_TAG_FORMAT = re.compile(r'{(.*?)}')
    __CUSTOM_NONINCREMENTAL_TAG_QUICK_REPLACE = lambda tag: '{' + str(tag) + '}'

    __CSV_TAG_HEADLINE = 'Tag'
    __CSV_ELAPSED_TIME_HEADLINE = 'Elapsed Time'

    def __init__(self, debug=False, autostart=False, custom_tags=True, rounding_precision=None):
        """
        StopWatch initialization
        :param debug: Whether StopWatch is in debug mode or not. Does nothing at the moment.
        :param autostart: Starts the StopWatch automatically if set to 'True'
        :param custom_tags: Whether custom_tags are enabled or disabled (to gain performance)
        :param rounding_precision: Number of decimal digits to be stored. None means all.
        """
        self.probes = OrderedDict()
        self.probes_n = 0
        self.debug_mode = debug
        self.custom_tags = defaultdict(lambda: 0)
        self.custom_tags_enabled = custom_tags
        self.rounding_precision = rounding_precision

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

        if self.rounding_precision is not None:
            self.probes[tag] = round(self.probes[tag], self.rounding_precision)

        return self.probes[tag]

    def pprint_probes(self, exponential_format=False):
        """
        Pretty prints all probes registered up to now.
        :param exponential_format: Whether exponential float representation format will be used or not
        :return:
        """
        float_format = "{:s}\t\t{:g}" if exponential_format else "{:s}\t\t{:f}"
        maxlen = len(max(self.probes.keys(), key=len))
        print("\n\n{:s}\t\t{:s}\n".format("TAG".ljust(maxlen, " "), "ELAPSED TIME"))

        for tag, elapsed_time in self.probes.items():
            print(float_format.format(tag.ljust(maxlen, " "), elapsed_time))

    def csv_dump(self, filepath="", exponential_format=False):
        """
        Dumps all probe information to a csv file
        :param filepath: Path to the taget file
        :param exponential_format: Whether exponential float representation format will be used or not
        :return:
        """
        with open(filepath, 'w', newline='') as csvfile:
            self.__write_csv(csvfile, exponential_format=exponential_format)

    def csv_dumps(self, exponential_format=False):
        """
        Dumps all probe information into a csv formatted string
        :param exponential_format: Whether exponential float representation format will be used or not
        :return: String with csv encoded information about the probes
        """
        result = self.__write_csv(StringIO(), exponential_format=exponential_format)
        return result.getvalue()

    def __write_csv(self, file, exponential_format=False):
        """
        Writes all probe information to a generic file
        :param file: Input file
        :param exponential_format: Whether exponential float representation format will be used or not
        :return: File used to write all information
        """
        float_format = "{:g}" if exponential_format else "{:f}"
        fieldnames = [StopWatch.__CSV_TAG_HEADLINE, StopWatch.__CSV_ELAPSED_TIME_HEADLINE]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for tag, elapsed_time in self.probes.items():
            writer.writerow({StopWatch.__CSV_TAG_HEADLINE: tag, StopWatch.__CSV_ELAPSED_TIME_HEADLINE: float_format.format(elapsed_time)})
        return file

    def __populate_custom_tag(self, tag):
        """
        Populates a tag with custom tags if available
        :param tag: Unpopulated tag
        :return: Populated tag
        """
        tag = self.__populate_custom_autoincrement_tag(tag)
        tag = self.__populate_custom_nonincremental_tag(tag)
        return tag

    def __populate_custom_autoincrement_tag(self, tag):
        """
        Checks if autoincrement custom tags are present and populates them
        :param tag: Unpopulated tag
        :return: Populated tag
        """
        found_tags = StopWatch.__CUSTOM_AUTOINCREMENT_TAG_FORMAT.findall(tag)
        if not found_tags:
            return tag
        for found_tag in found_tags:
            tag = tag.replace(StopWatch.__CUSTOM_AUTOINCREMENT_TAG_QUICK_REPLACE(found_tag),
                              str(self.custom_tags[found_tag]))
            self.custom_tags[found_tag] += 1
        return tag

    def __populate_custom_nonincremental_tag(self, tag):
        """
        Checks for non incremental custom tags and populates them
        :param tag:Unpopulated tag
        :return: Populated tag
        """
        found_tags = StopWatch.__CUSTOM_NONINCREMENTAL_TAG_FORMAT.findall(tag)
        if not found_tags:
            return tag
        for found_tag in found_tags:
            tag = tag.replace(StopWatch.__CUSTOM_NONINCREMENTAL_TAG_QUICK_REPLACE(found_tag),
                              str(self.custom_tags[found_tag]))
        return tag

    @property
    def elapsed_time(self):
        """
        Elapsed time from starting time to finished time. If the stopwatch is still running it takes now as the finished time.
        :return: Elapsed time
        """
        aux = time.time()
        return self.probes.get(StopWatch.__STOP_PROBE_TAG, aux) - self.probes.get(StopWatch.__START_PROBE_TAG, aux)
