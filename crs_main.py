from crs_data import Data
from data_sorter import DataSorter, ScheduleGenerator

data_class = Data()
data: list[dict[str, str | list[str]]] = data_class.data()

data_sorter = DataSorter(data)
data_sorter.sort_data()
data_sorter.display_data(data_sorter.subjects_with_time)

data_generator = ScheduleGenerator(data_sorter.subjects_with_time)
# print(data_generator.check_conflict([{'Day': 'WF', 'Time': '10-11:30AM', 'Room': 'lec AECH-Accenture'}], [{'Day': 'TF', 'Time': '1-12:15PM', 'Room': 'disc NIP'}]))
# schedules: list[list[dict[Course, Section]]] = data_generator.generate_schedules(data_sorter.subjects_with_time, [])