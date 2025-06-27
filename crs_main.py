# Unoptimized libraries
# from crs_scraper.crscraper_preenlistment import CRScraperPreEnlistment
# from crs_scraper.crscraper_student_registration import CRScraperStudentRegistration
# from crs_scraper.crs_data import Data
# from crs_scraper.data_sorter import DataSorter, ScheduleGenerator

# For .env
from dotenv import load_dotenv

# Load .env into os.environ
load_dotenv()

# Optimized libraries
from crs_scraper.optimized_crscraper_preenlistment import CRScraperPreEnlistment
from crs_scraper.optimized_crscraper_student_registration import CRScraperStudentRegistration
from crs_scraper.data_sorter import ScheduleGenerator

from flask import Flask, Response, jsonify, make_response, url_for, request, session
from flask_cors import CORS
import csv
import os
from requests import Session
from requests.cookies import RequestsCookieJar
from requests.utils import dict_from_cookiejar

# Login with Google OAuth feature
from authlib.integrations.flask_client import OAuth
from bs4 import BeautifulSoup
from requests.utils import cookiejar_from_dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ------------------------------------------------------------
app = Flask("CRScraper") 
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.config['DEBUG'] = True

# Login with Google OAuth feature
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config.update({
    "GOOGLE_CLIENT_ID":     os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
    "GOOGLE_DISCOVERY_URL": os.getenv("GOOGLE_DISCOVERY_URL"),
})

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url=app.config["GOOGLE_DISCOVERY_URL"],
    client_kwargs={ "scope": "openid email profile" },
)
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

# test https://crs.upd.edu.ph/student_registration/class_search/18843, https://crs.upd.edu.ph/student_registration/class_search/14732

all_course_table_schedule_url: list[str] = []
crs_username_global = ""
crs_password_global = ""
clicked_login_with_google = False
# ------------------------------------------------------------


# ------------------------------------------------------------
@app.route('/login', methods=['POST'])
def login() -> Response:
    """
    DEPRECATED: Due to CRS new login feature.
    """
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


@app.route('/login-with-gmail')
def login_with_google():
    # Render a helper page telling the user to log in on CRS
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>CRS Login</title>
      <style>
        body {
          font-family: sans-serif;
          text-align: center;
        }
        .box {
          display: inline-block;
          padding: 1.5rem;
          border: 2px solid #444;
          border-radius: 8px;
        }
      </style>
    </head>
    <body>
      <div class="box">
        <h2>⚙️ Redirecting to CRS…</h2>
        <p>Please complete your UP Mail login in the new window.</p>
        <p>If you don’t see anything, check your pop-up blocker.</p>
        <p>Note: This is for authentication purposes.</p>
      </div>
      <script>
        // Kick off the real login handshake after a short pause
        setTimeout(() => {
          // change location to the actual OAuth endpoint
          window.location.href = '/_continue_crs_oauth';
        }, 1000);
      </script>
    </body>
    </html>
    """
    return html


@app.route('/_continue_crs_oauth')
def _continue_crs_oauth() -> Response:
    global clicked_login_with_google
    clicked_login_with_google = True

    # Instantiate your scraper (no need for username/password here)
    scraper = CRScraperPreEnlistment(
        login_url=login_url,
        username=None,
        password=None,
        all_course_table_schedule_url=all_course_table_schedule_url
    )

    # Delegate to your method—this will pop up Chrome for the user to log in,
    # complete 2FA, then harvest the CRS cookies back into scraper.session.
    scraper.login_with_google_token()

    # Now persist those cookies in Flask session for later `/scrape` use:
    session['crs_selenium_cookies'] = scraper._selenium_cookies
    app.logger.debug(f"Selenium gave: {session.get('crs_selenium_cookies')!r}")

    # # Seamless Login Idea:
    # scraper.login_with_id_token(id_token)
    # session['crs_cookies_dict'] = dict_from_cookiejar(scraper.session.cookies)
    # app.logger.debug(f"Scraper cookies!: {session.get('crs_cookies_dict')!r}")

    # 5) Signal success back to the SPA
    return make_response("""
    <script>
      window.opener.postMessage({ status: 'success' }, 'http://localhost:3000');
      window.close();
    </script>
    """, 200)


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
    if clicked_login_with_google:
        raw = session.get('crs_selenium_cookies')
        if not raw:
            return make_response(jsonify({"status":"failure","message":"Not logged in"}), 401)

        jar = RequestsCookieJar()
        for c in raw:
            jar.set(
                name   = c['name'],
                value  = c['value'],
                domain = c.get('domain', 'crs.upd.edu.ph'),
                path   = c.get('path', '/'),
                secure = c.get('secure', False),
                rest   = {'HttpOnly': c.get('httpOnly', False)}
            )

        s = Session()
        s.cookies = jar

        # Debug: log what cookies will be sent
        app.logger.debug(f"Requests sends: {s.cookies.items()}")

        # debug: confirm you’re still logged in
        r = s.get("https://crs.upd.edu.ph/user/view/classmessages")
        open("debug_after_rebuild.html","w",encoding="utf8").write(r.text)

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
        if clicked_login_with_google:
            crs_scraper.session = s
            data = crs_scraper.main_with_email()
        else:
            data = crs_scraper.main()
    elif "student_registration" in all_course_table_schedule_url[0]:
        crs_scraper = CRScraperStudentRegistration(login_url, crs_username_global, crs_password_global, all_course_table_schedule_url)
        if clicked_login_with_google:
            crs_scraper.session = s
            data = crs_scraper.main_with_email()
        else:
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

    app.logger.debug(f"Raw schedules from generator: {schedules!r}")

    ranked_schedules = data_generator.rank_by_probability(schedules)
    # data_generator.display_all_possible_schedules(ranked_schedules)
    data_generator.convert_to_csv(ranked_schedules, "schedules_ranked.csv")

    app.logger.debug(f"Ranked schedules from generator: {ranked_schedules!r}")

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

