# these are sample ME courses
# https://crs.upd.edu.ph/preenlistment/class_search/18918, https://crs.upd.edu.ph/preenlistment/class_search/18918, https://crs.upd.edu.ph/preenlistment/class_search/18913, https://crs.upd.edu.ph/preenlistment/class_search/18916, https://crs.upd.edu.ph/preenlistment/class_search/106, https://crs.upd.edu.ph/preenlistment/class_search/18915

from crs_scraper.crscraper_preenlistment import CRScraper
from crs_scraper.data_sorter import DataSorter, ScheduleGenerator 

login_url = "https://crs.upd.edu.ph/"
crs_username_global = input()
crs_password_global = input()
all_course_table_schedule_url = ["https://crs.upd.edu.ph/preenlistment/class_search/18918", 
                                 "https://crs.upd.edu.ph/preenlistment/class_search/18918", 
                                 "https://crs.upd.edu.ph/preenlistment/class_search/18913",
                                 "https://crs.upd.edu.ph/preenlistment/class_search/18916",
                                 "https://crs.upd.edu.ph/preenlistment/class_search/106",
                                 "https://crs.upd.edu.ph/preenlistment/class_search/18915"
                                 ] # you can change this

crscraper = CRScraper(login_url, crs_username_global, crs_password_global, all_course_table_schedule_url)
data = crscraper.main()

if data:
    data_sorter = DataSorter(data)
    data_sorter.sort_data()
    # data_sorter.display_data(data_sorter.subjects_with_time)

    data_generator = ScheduleGenerator(data_sorter.subjects_with_time)
    schedules = data_generator.generate_schedules(data_sorter.subjects_with_time)
    # data_generator.display_all_possible_schedules(schedules)

    ranked_schedules = data_generator.rank_by_probability(schedules)
    # data_generator.display_all_possible_schedules(ranked_schedules)
    data_generator.convert_to_csv(ranked_schedules, "schedules_ranked_test.csv")