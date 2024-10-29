from crs_data import Data
from data_sorter import DataSorter, ScheduleGenerator, ListOfCoursesWithTime
# from crscraper import CRScraper

# login_url = "https://crs.upd.edu.ph/"
# all_course_table_schedule_url = ["https://crs.upd.edu.ph/student_registration/class_search/5670", 
#                                         "https://crs.upd.edu.ph/student_registration/class_search/18849", 
#                                         "https://crs.upd.edu.ph/student_registration/class_search/18843",
#                                         "https://crs.upd.edu.ph/student_registration/class_search/19401",
#                                         "https://crs.upd.edu.ph/student_registration/class_search/19395"
#                                         ]

# crs_username = input("Enter CRS Username: ")
# crs_password = input("Enter CRS Password: ")

# crs_scraper = CRScraper(login_url, crs_username, crs_password, all_course_table_schedule_url)

# data = crs_scraper.main() # This should replace the data variable
data_class = Data()
data: list[dict[str, str | list[str]]] = data_class.data()

data_sorter = DataSorter(data)
data_sorter.sort_data()
# data_sorter.display_data(data_sorter.subjects_with_time)

data_generator = ScheduleGenerator(data_sorter.subjects_with_time)
schedules: list[ListOfCoursesWithTime] = data_generator.generate_schedules(data_sorter.subjects_with_time)
data_generator.display_all_possible_schedules(schedules)
# data_generator.convert_to_csv(schedules)