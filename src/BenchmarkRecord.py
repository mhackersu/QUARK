#  Copyright 2021 The QUARK Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import final
from collections import deque
import json
from copy import deepcopy

from Metrics import Metrics


class BenchmarkRecord:
    """
    The BenchmarkRecord class contains all the Metric instances and additional general information
    generated by a single benchmark run.
    """

    # pylint: disable=R0917
    def __init__(self, benchmark_backlog_item_number: int, timestamp: str, git_revision_number: str,
                 git_uncommitted_changes: str, repetition: int, total_repetitions: int):
        """
        Constructor method for BenchmarkRecord.

        :param benchmark_backlog_item_number: Number of the item in the benchmark backlog
        :param timestamp: Timestamp of the benchmark run
        :param git_revision_number: Git revision number during the benchmark run
        :param git_uncommitted_changes: Indication if there were uncommitted changes during the benchmark run
        :param repetition: Number of current repetitions of the benchmark run
        :param total_repetitions: Number of total repetitions of the benchmark run
        """
        self.benchmark_backlog_item_number = benchmark_backlog_item_number
        self.timestamp = timestamp
        self.git_revision_number = git_revision_number
        self.git_uncommitted_changes = git_uncommitted_changes
        self.repetition = repetition
        self.total_repetitions = total_repetitions
        self.total_time = None
        self.total_time_unit = "ms"
        self.linked_list_metrics = deque()

    @final
    def append_module_record_right(self, module_record: Metrics) -> None:
        """
        Adds Metrics instance to the end of the linked list.

        :param module_record: Metrics instance which should be appended to the end of the linked list
        """
        self.linked_list_metrics.append(module_record)

    @final
    def append_module_record_left(self, module_record: Metrics) -> None:
        """
        Adds Metrics instance to the beginning of the linked list.

        :param module_record: Metrics instance which should be appended to the beginning of the linked list
        """
        self.linked_list_metrics.appendleft(module_record)

    @final
    def sum_up_times(self) -> None:
        """
        Sums up the recording timings.
        """
        self.total_time = sum(item.total_time for item in self.linked_list_metrics)

    @final
    def hash_config(self, llist: deque) -> dict:
        """
        Recursively traverses through linked list and returns a dictionary with the next module's name, config,
        and subsequent submodule(s).

        :param llist: Linked list
        :return: Dictionary with the name and config of the first module in the linked list and subsequent submodule(s)
        """
        next_item: Metrics = llist.popleft()
        return {
            "module_name": next_item.module_name,
            "module_config": next_item.module_config,
            "submodule": self.hash_config(llist) if llist else {}
        }

    @final
    def start_hash_config(self) -> int:
        """
        Recursively creates dictionary containing the name of the module and its config for all modules in a chain.
        Then generates hash with it.

        :return: Hash of the benchmark run config
        """
        list_copy = deepcopy(self.linked_list_metrics)
        # Hash assumes that all keys are strings!
        return hash(json.dumps(self.hash_config(list_copy), sort_keys=True))

    @final
    def linked_list_to_dict(self, llist: deque, module_level: int = 0) -> dict:
        """
        Recursively traverses through linked list and adds the items of the Metrics objects to one single dictionary.

        :param llist: Linked list
        :param module_level: Current level in chain (starts at 0)
        :return: Dictionary with the module, its level, and its submodule(s)
        """
        next_item: Metrics = llist.popleft()
        return {
            **next_item.get(),
            "module_level": module_level,
            "submodule": self.linked_list_to_dict(llist, module_level + 1) if llist else {}
        }

    @final
    def start_linked_list_to_dict(self) -> dict:
        """
        Helper function to start linked_list_to_dict function which merges the various Metrics objects
        to one dictionary.

        :return: Resulting dictionary of linked_list_to_dict
        """
        list_copy = deepcopy(self.linked_list_metrics)
        return self.linked_list_to_dict(list_copy)

    @final
    def get(self) -> dict:
        """
        Returns a dictionary containing all benchmark information and a nested dictionary in which each level
        contains the metrics of the respective module.

        :return: Dictionary containing all the records of the benchmark
        """
        return {
            "benchmark_backlog_item_number": self.benchmark_backlog_item_number,
            "timestamp": self.timestamp,
            "config_hash": self.start_hash_config(),
            "total_time": self.total_time,
            "total_time_unit": self.total_time_unit,
            "git_revision_number": self.git_revision_number,
            "git_uncommitted_changes": self.git_uncommitted_changes,
            "repetition": self.repetition,
            "total_repetitions": self.total_repetitions,
            "module": self.start_linked_list_to_dict()
        }

    @final
    def copy(self) -> "BenchmarkRecord":
        """
        Returns a copy of itself.

        :return: Return copy of itself
        """
        return deepcopy(self)


class BenchmarkRecordStored:
    """
    This class can be used to store the BenchmarkRecord of a previous QUARK run as read from results.json.
    It is a simple wrapper with the purpose to provide the same interface to the BenchmarkManager as the
    BenchmarkRecord does.
    """

    def __init__(self, record: dict):
        """
        Constructor method for BenchmarkRecordStored.

        :param record: the record as dictionary
        """
        self.record = record

    def get(self) -> dict:
        """
        Simply returns the dictionary as given to the constructor.

        :return: Dictionary as given to the constructor
        """
        return self.record

    def sum_up_times(self) -> None:
        """
        Dummy implementation which does nothing.
        """
        pass
