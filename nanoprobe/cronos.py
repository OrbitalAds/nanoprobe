import time
import csv
from io import StringIO

from collections import OrderedDict


class StopWatch:
    __START_PROBE_TAG = 'start'
    __STOP_PROBE_TAG = 'stop'
    __DEFAULT_CLICK_TAG_FORMAT = 'click-{:d}'

    __CSV_TAG_HEADLINE = 'Tag'
    __CSV_ELAPSED_TIME_HEADLINE = 'Elapsed Time'

    def __init__(self, debug=False, autostart=False):
        self.__probes = OrderedDict()
        self.__probes_n = 0
        self.__debug_mode = debug
        if autostart:
            self.start()

    def start(self):
        """
        Starts the stopwatch
        :return:
        """
        self.__probes[StopWatch.__START_PROBE_TAG] = time.time()

    def stop(self):
        """
        Stops the stopwatch
        :return:
        """
        self.__probes[StopWatch.__STOP_PROBE_TAG] = time.time()

    def click(self, tag=None):
        """
        Stores elapsed time from the start of the stopwatch time untill this moment.
        If StopWatch wasn't already running it starts it.
        :param tag: Probe's tag. If not present it will choose 'default'
        :return:
        """
        if not tag:
            tag = StopWatch.__DEFAULT_CLICK_TAG_FORMAT.format(self.__probes_n)
            self.__probes_n += 1

        aux = time.time()
        if StopWatch.__START_PROBE_TAG not in self.__probes:
            self.__probes[StopWatch.__START_PROBE_TAG] = aux

        self.__probes[tag] = aux - self.__probes[StopWatch.__START_PROBE_TAG]

        return self.__probes[tag]

    def pprint_probes(self):
        """
        Pretty prints all probes registered up to now.
        :return:
        """

        print("TAG\t\t\t ELAPSED TIME")
        print("---\t\t\t ------------\n")
        for tag, elapsed_time in self.__probes.items():
            print(tag+"\t\t", elapsed_time)

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
        for tag, elapsed_time in self.__probes.items():
            writer.writerow({StopWatch.__CSV_TAG_HEADLINE: tag, StopWatch.__CSV_ELAPSED_TIME_HEADLINE: elapsed_time})
        return file


    @property
    def elapsed_time(self):
        """
        Elapsed time from starting time to finished time. If the stopwatch is still running it takes now as the finished time.
        :return: Elapsed time
        """
        aux = time.time()
        return self.__probes.get(StopWatch.__STOP_PROBE_TAG, aux) - self.__probes.get(StopWatch.__START_PROBE_TAG, aux)

