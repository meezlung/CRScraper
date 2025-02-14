# Unoptimized libraries
# from crs_scraper.crscraper_preenlistment import CRScraperPreEnlistment
# from crs_scraper.crscraper_student_registration import CRScraperStudentRegistration
# from crs_scraper.crs_data import Data
# from crs_scraper.data_sorter import DataSorter, ScheduleGenerator

# Optimized libraries
from crs_scraper.optimized_crscraper_preenlistment import CRScraperPreEnlistment
from crs_scraper.optimized_crscraper_student_registration import CRScraperStudentRegistration
from crs_scraper.data_sorter import ScheduleGenerator

from flask import Flask, Response, jsonify, make_response, request
from flask_cors import CORS
import csv
import os

# ------------------------------------------------------------
app = Flask(__name__) 
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['DEBUG'] = True
# ------------------------------------------------------------


# ------------------------------------------------------------
login_url = "https://crs.upd.edu.ph/"

# ------------------------------------------------------------
# preenlistment
# 2nd year 1st sem
# https://crs.upd.edu.ph/preenlistment/class_search/5670, https://crs.upd.edu.ph/preenlistment/class_search/18849, https://crs.upd.edu.ph/preenlistment/class_search/18843, https://crs.upd.edu.ph/preenlistment/class_search/19401, https://crs.upd.edu.ph/preenlistment/class_search/19395

# 2nd year 2nd sem
# gab
# https://crs.upd.edu.ph/preenlistment/class_search/19405, https://crs.upd.edu.ph/preenlistment/class_search/19398, https://crs.upd.edu.ph/preenlistment/class_search/19403, https://crs.upd.edu.ph/preenlistment/class_search/19404, https://crs.upd.edu.ph/preenlistment/class_search/19480

# micka
# https://crs.upd.edu.ph/preenlistment/class_search/18918, https://crs.upd.edu.ph/preenlistment/class_search/18918, https://crs.upd.edu.ph/preenlistment/class_search/18913, https://crs.upd.edu.ph/preenlistment/class_search/18916, https://crs.upd.edu.ph/preenlistment/class_search/106, https://crs.upd.edu.ph/preenlistment/class_search/18915, https://crs.upd.edu.ph/preenlistment/class_search/1932
# ------------------------------------------------------------

# ------------------------------------------------------------
# student registration
# sample ME courses
# https://crs.upd.edu.ph/student_registration/class_search/18918, https://crs.upd.edu.ph/student_registration/class_search/18918, https://crs.upd.edu.ph/student_registration/class_search/18913, https://crs.upd.edu.ph/student_registration/class_search/18916, https://crs.upd.edu.ph/student_registration/class_search/106, https://crs.upd.edu.ph/student_registration/class_search/18915

# sample CS courses
# https://crs.upd.edu.ph/student_registration/class_search/19405, https://crs.upd.edu.ph/student_registration/class_search/19398, https://crs.upd.edu.ph/student_registration/class_search/19403, https://crs.upd.edu.ph/student_registration/class_search/19404, https://crs.upd.edu.ph/student_registration/class_search/19480
# ------------------------------------------------------------

all_course_table_schedule_url: list[str] = []
crs_username_global = ""
crs_password_global = ""
# ------------------------------------------------------------


# ------------------------------------------------------------
@app.route('/login', methods=['POST'])
def login() -> Response:
    global crs_username_global, crs_password_global

    credentials = request.json
    print("Received credentials:", credentials)
    if credentials:
        crs_username = credentials['username']
        crs_password = credentials['password']

        if not crs_username or not crs_password:
            # Return a failure response with a 400 status code using make_response
            response = make_response(jsonify({"message": "Missing username or password", "status": "failure"}), 400)
            return response

        crs_username_global = crs_username
        crs_password_global = crs_password

        # Use any of the crscraper with the login credentials
        crs_scraper = CRScraperPreEnlistment(login_url, crs_username, crs_password, all_course_table_schedule_url)
        crs_scraper.login_into_crs() # Just to authenticate the user

        app.logger.debug(f"Login successful as {crs_username}!")
    
        # Return a success response with a 200 status code using make_response
        response = make_response(jsonify({"message": "Login successful", "status": "success"}), 200)
        return response

    # Return a failure response with a 400 status code using make_response
    response = make_response(jsonify({"message": "Missing credentials", "status": "failure"}), 400)
    return response


@app.route('/set-urls', methods=['POST'])
def set_urls() -> Response:
    global all_course_table_schedule_url
    data = request.get_json()
    app.logger.debug(f"Received data {data}!")

    # Retrieve and store the course links submitted by the user
    if data:
        links = data['links']
        all_course_table_schedule_url = [link.strip() for link in links.split(",") if link.strip()]

        # Return a success response with a 200 status code using make_response
        response = make_response(jsonify({"message": "Course links set successfully", "status": "success"}), 200)
        return response
    
    # Return a failure response with a 400 status code using make_response
    response = make_response(jsonify({"message": "Missing course links", "status": "failure"}), 400)
    return response


@app.route('/scrape', methods=['POST'])
def scrape() -> Response:
    global crs_username_global, crs_password_global, all_course_table_schedule_url

    if not all_course_table_schedule_url:
        # Return a failure response with a 400 status code using make_response
        response = make_response(jsonify({"message": "No course links set yet", "status": "failure"}), 400)
        return response

    app.logger.debug(f"Scraping data for {crs_username_global} with course links {all_course_table_schedule_url}!")

    # ----------------------------------------------------------------
    data = None

    # Know if the links are preentlistment or student registration
    if "preenlistment" in all_course_table_schedule_url[0]:
        crs_scraper = CRScraperPreEnlistment(login_url, crs_username_global, crs_password_global, all_course_table_schedule_url)
        data = crs_scraper.main()
    elif "student_registration" in all_course_table_schedule_url[0]:
        crs_scraper = CRScraperStudentRegistration(login_url, crs_username_global, crs_password_global, all_course_table_schedule_url)
        data = crs_scraper.main()
    # ----------------------------------------------------------------

    # Scraping logic
    if not data:
        # Return a failure response with a 400 status code using make_response
        response = make_response(jsonify({"message": "Failed to retrieve course data. Please try again", "status": "failure"}), 400)
        return response

    app.logger.debug(f"Data scraped successfully! {data}")

    # # For now, we simulate succesful login and scraping data
    # data_class = Data()
    # data = data_class.data() 

    data_generator = ScheduleGenerator(data)
    schedules = data_generator.generate_schedules(data)
    # data_generator.display_all_possible_schedules(schedules)

    ranked_schedules = data_generator.rank_by_probability(schedules)
    # data_generator.display_all_possible_schedules(ranked_schedules)
    data_generator.convert_to_csv(ranked_schedules, "schedules_ranked.csv")

    app.logger.debug(f"Schedules generated and ranked successfully in schedules_ranked.csv! {ranked_schedules}")

    # Return a success response with a 200 status code using make_response
    response = make_response(jsonify({"message": "Schedule data generated", "status": "success"}), 200)
    return response


@app.route('/get-schedule', methods=['GET'])
def get_schedule():
    if not os.path.isfile('schedules_ranked.csv'):
        return jsonify({"message": "No schedules found yet.", "status": "failure"})
    
    with open('schedules_ranked.csv', 'r') as file:
        reader = csv.DictReader(file)
        schedules = [row for row in reader]
    return jsonify(schedules)

if __name__ == '__main__':
    # data_class = Data()
    # data = data_class.data()

    # data_sorter = DataSorter(data)
    # data_sorter.sort_data()
    # # data_sorter.display_data(data_sorter.subjects_with

    # data_generator = ScheduleGenerator(data_sorter.subjects_with_time)
    # schedules = data_generator.generate_schedules(data_sorter.subjects_with_time)
    # # data_generator.display_all_possible_schedules(schedules)

    # ranked_schedules = data_generator.rank_by_probability(schedules)
    # # data_generator.display_all_possible_schedules(ranked_schedules)
    # data_generator.convert_to_csv(ranked_schedules, "schedules_ranked.csv")
    app.run(host='0.0.0.0', port=8080)
# ------------------------------------------------------------

