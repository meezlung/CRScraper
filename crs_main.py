from crs_data import Data
from data_sorter import DataSorter, ScheduleGenerator, ListOfCoursesWithTime

# type: oign

data_class = Data()
data: list[dict[str, str | list[str]]] = data_class.data()

data_sorter = DataSorter(data)
data_sorter.sort_data()
# data_sorter.display_data(data_sorter.subjects_with_time)

data_generator = ScheduleGenerator(data_sorter.subjects_with_time)
schedules: list[ListOfCoursesWithTime] = data_generator.generate_schedules(data_sorter.subjects_with_time)
data_generator.display_all_possible_schedules(schedules)