from crs_scraper.crs_data import Data
from crs_scraper.data_sorter import DataSorter, ScheduleGenerator, ListOfCoursesWithTime
from flask import Flask, jsonify
from flask_cors import CORS
import csv

# ------------------------------------------------------------
# from crs_scraper.crscraper import CRScraper

# login_url = "https://crs.upd.edu.ph/"
# all_course_table_schedule_url = ["https://crs.upd.edu.ph/student_registration/class_search/5670", 
                                 # "https://crs.upd.edu.ph/student_registration/class_search/18849", 
                                 # "https://crs.upd.edu.ph/student_registration/class_search/18843",
                                 # "https://crs.upd.edu.ph/student_registration/class_search/19401",
                                 # "https://crs.upd.edu.ph/student_registration/class_search/19395"
                                 # ]

# crs_username = input("Enter CRS Username: ")
# crs_password = input("Enter CRS Password: ")

# crs_scraper = CRScraper(login_url, crs_username, crs_password, all_course_table_schedule_url)

# data = crs_scraper.main() # This should replace the data variable
# ------------------------------------------------------------


data_class = Data() 
data: list[dict[str, str | list[str]]] = data_class.data()

data_sorter = DataSorter(data)
data_sorter.sort_data()
# data_sorter.display_data(data_sorter.subjects_with_time)

data_generator = ScheduleGenerator(data_sorter.subjects_with_time)
schedules: list[ListOfCoursesWithTime] = data_generator.generate_schedules(data_sorter.subjects_with_time)
# data_generator.display_all_possible_schedules(schedules)

ranked_schedules = data_generator.rank_by_probability(schedules)
# data_generator.display_all_possible_schedules(ranked_schedules)
data_generator.convert_to_csv(ranked_schedules, "schedules_ranked.csv")

# ------------------------------------------------------------
app = Flask(__name__) 
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/get-schedule', methods=['GET'])
def get_schedule():
    with open('schedules_ranked.csv', 'r') as file:
        reader = csv.DictReader(file)
        schedules = [row for row in reader]
    return jsonify(schedules)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
# ------------------------------------------------------------

