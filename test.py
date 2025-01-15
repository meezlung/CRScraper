# Search for your preferred courses in CRS's Preenlistment tab and input the URLs in the list below

# -------------------------------------------------------------------------
# preenlistment links
# sample ME courses
# https://crs.upd.edu.ph/preenlistment/class_search/18918, https://crs.upd.edu.ph/preenlistment/class_search/18918, https://crs.upd.edu.ph/preenlistment/class_search/18913, https://crs.upd.edu.ph/preenlistment/class_search/18916, https://crs.upd.edu.ph/preenlistment/class_search/106, https://crs.upd.edu.ph/preenlistment/class_search/18915

# sample CS courses
# https://crs.upd.edu.ph/preenlistment/class_search/19405, https://crs.upd.edu.ph/preenlistment/class_search/19398, https://crs.upd.edu.ph/preenlistment/class_search/19403, https://crs.upd.edu.ph/preenlistment/class_search/19404, https://crs.upd.edu.ph/preenlistment/class_search/19480
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# student registration links
# sample ME courses
# https://crs.upd.edu.ph/student_registration/class_search/18918, https://crs.upd.edu.ph/student_registration/class_search/18918, https://crs.upd.edu.ph/student_registration/class_search/18913, https://crs.upd.edu.ph/student_registration/class_search/18916, https://crs.upd.edu.ph/student_registration/class_search/106, https://crs.upd.edu.ph/student_registration/class_search/18915

# sample CS courses
# https://crs.upd.edu.ph/student_registration/class_search/19405, https://crs.upd.edu.ph/student_registration/class_search/19398, https://crs.upd.edu.ph/student_registration/class_search/19403, https://crs.upd.edu.ph/student_registration/class_search/19404, https://crs.upd.edu.ph/student_registration/class_search/19480
# -------------------------------------------------------------------------


from crs_scraper.optimized_crscraper_preenlistment import CRScraperPreEnlistment
from crs_scraper.optimized_crscraper_student_registration import CRScraperStudentRegistration
from crs_scraper.data_sorter import ScheduleGenerator 
from getpass import getpass # This is just used to hide the password input when typing in the terminal (https://docs.python.org/3/library/getpass.html)
import json

login_url = "https://crs.upd.edu.ph/"
crs_username_global = input("CRS Username: ")
crs_password_global = getpass("CRS Password: ")

# Ask input from the terminal
all_course_table_schedule_urls = input("Enter the course table schedule URLs separated by comma: ").split(",") # sample format

all_course_table_schedule_url_test = [""]

if not all_course_table_schedule_urls:
    raise ValueError("No course table schedule URLs found.")

filename = "invalid.csv"
data = None

if all_course_table_schedule_urls[0] and "preenlistment" in all_course_table_schedule_urls[0]: # if preenlistment link/s
    filename = "schedules_ranked_test_preenlistment.csv"
    crscraper = CRScraperPreEnlistment(login_url, crs_username_global, crs_password_global, all_course_table_schedule_urls)
    data = crscraper.main()

elif all_course_table_schedule_urls[0] and "student_registration" in all_course_table_schedule_urls[0]: # if student registration link/s
    filename = "schedules_ranked_test_student_registration.csv"
    crscraper = CRScraperStudentRegistration(login_url, crs_username_global, crs_password_global, all_course_table_schedule_urls)
    data = crscraper.main()

if not data:
    raise ValueError("No data found. Please check the course URLs provided. Note: Also check if it's a preenlistment or student registration link.")

print("Data has been scraped succesfully.")
print()

# Print data beautifully in the terminal
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
