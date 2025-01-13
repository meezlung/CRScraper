# Search for your preferred courses in CRS's Student Registration tab and input the URLs in the list below

# sample ME courses
# https://crs.upd.edu.ph/student_registration/class_search/18918, https://crs.upd.edu.ph/student_registration/class_search/18918, https://crs.upd.edu.ph/student_registration/class_search/18913, https://crs.upd.edu.ph/student_registration/class_search/18916, https://crs.upd.edu.ph/student_registration/class_search/106, https://crs.upd.edu.ph/student_registration/class_search/18915

# sample CS courses
# https://crs.upd.edu.ph/student_registration/class_search/19405, https://crs.upd.edu.ph/student_registration/class_search/19398, https://crs.upd.edu.ph/student_registration/class_search/19403, https://crs.upd.edu.ph/student_registration/class_search/19404, https://crs.upd.edu.ph/student_registration/class_search/19480

from crs_scraper.optimized_crscraper_student_registration import CRScraper
from crs_scraper.data_sorter import ScheduleGenerator
from getpass import getpass # This is used to hide the password input when typing in the terminal (https://docs.python.org/3/library/getpass.html)
import json

login_url = "https://crs.upd.edu.ph/"
crs_username_global = input("CRS Username: ")
crs_password_global = getpass("CRS Password: ")

all_course_table_schedule_url_me = ["https://crs.upd.edu.ph/student_registration/class_search/18918", 
                                 "https://crs.upd.edu.ph/student_registration/class_search/18918", 
                                 "https://crs.upd.edu.ph/student_registration/class_search/18913",
                                 "https://crs.upd.edu.ph/student_registration/class_search/18916",
                                 "https://crs.upd.edu.ph/student_registration/class_search/106",
                                 "https://crs.upd.edu.ph/student_registration/class_search/18915"
                                 ] # sample format

all_course_table_schedule_url_cs = ["https://crs.upd.edu.ph/student_registration/class_search/19405", 
                                 "https://crs.upd.edu.ph/student_registration/class_search/19398", 
                                 "https://crs.upd.edu.ph/student_registration/class_search/19403",
                                 "https://crs.upd.edu.ph/student_registration/class_search/19404",
                                 "https://crs.upd.edu.ph/student_registration/class_search/19480",
                                 ] # sample format

all_course_table_schedule_url_test = [""]

filename = "schedules_ranked_test_student_registration.csv"

crscraper = CRScraper(login_url, crs_username_global, crs_password_global, all_course_table_schedule_url_cs)
data = crscraper.main()

print("Data has been scraped succesfully.")
print()

# Print data beautifully
print(json.dumps(data, indent=1))
print()

if data:
    data_generator = ScheduleGenerator(data)
    schedules = data_generator.generate_schedules(data)
    # data_generator.display_all_possible_schedules(schedules)

    ranked_schedules = data_generator.rank_by_probability(schedules)
    # data_generator.display_all_possible_schedules(ranked_schedules)
    data_generator.convert_to_csv(ranked_schedules, filename)

    print(f"Ranked schedules saved to {filename}.")
    print()
