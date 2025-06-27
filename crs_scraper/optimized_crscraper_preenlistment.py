import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Optional, Union
from crs_scraper.probability_calculator import ProbabilityCalculator

# For Google OAuth Login
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import os
import tempfile, uuid

Course = str
Section = str
Schedule = list[dict[str, str | int | float]]
ListOfCoursesWithTime = list[dict[Course, list[dict[Section, Schedule]]]]

class CRScraperPreEnlistment:
    def __init__(self, 
                 login_url: str, username: str | None, password: str | None,    all_course_table_schedule_url: list[str], 
                 totp_secret: Optional[str] = None) -> None:
        self.username = username
        self.password = password
        self.login_url = login_url
        self.all_course_table_schedule_url = all_course_table_schedule_url
        self.totp_secret = totp_secret or os.getenv('GOOGLE_2FA_SECRET')

        self.preenlistment_priority = ""
        self.registration_priority = ""

        self.homepage_url = "https://crs.upd.edu.ph/user/view/classmessages"

        # Start a session
        self.session = requests.Session()
        self.data: ListOfCoursesWithTime = []  # Now in sorted format directly
        self.probability_calculator = ProbabilityCalculator()

    def main(self) -> Optional[ListOfCoursesWithTime]:
        print("Logging into CRS...")
        self.login_into_crs()
        print("Logged in successfully.")
        print()

        print("Getting priority...")
        self.get_priority()
        print()

        print("Accessing all possible course schedules...")
        self.access_all_possible_course_schedules()
        print("All possible course schedules accessed.")
        print()
        return self.data
    
    def main_with_email(self) -> Optional[ListOfCoursesWithTime]:
        print("Getting priority...")
        self.get_priority()
        print()

        print("Accessing all possible course schedules...")
        self.access_all_possible_course_schedules()
        print("All possible course schedules accessed.")
        print()
        return self.data

    def login_into_crs(self) -> None:
        # Get the login page to retrieve the CSRF token and any other hidden fields
        login_page = self.session.get(self.login_url)
        login_page.raise_for_status() # Ensure we got a successful response

        # Parse login page to find the form fields
        soup = BeautifulSoup(login_page.text, 'html.parser')

        # Find the CSRF token or other hidden fields if necessary
        csrf_token_candidate = soup.find('input', {'name': 'csrf_token'})

        # Ensure csrf_token_tag is either a Tag or None
        csrf_token_tag: Optional[Tag] = csrf_token_candidate if isinstance(csrf_token_candidate, Tag) else None

        csrf_value: Optional[Union[str, list[str]]] = ''

        if csrf_token_tag:
            csrf_value = csrf_token_tag.get('value', '')

        # Login credentials
        payload: dict[str, Optional[Union[str, list[str]]]] = {
            'txt_login': self.username,  # Replace with the actual form field name
            'pwd_password': self.password,  # Replace with the actual form field name
            'csrf_token': csrf_value,  # Include the CSRF token if required
            # Include any other hidden form fields that may be required
        }

        # Perform the login
        login_response = self.session.post(self.login_url, data=payload)
        login_response.raise_for_status()  # Ensure the login was successful

        if "Login Error" in login_response.text:  # Adjust the error message based on the site
            raise ValueError("Login failed: Invalid username or password")

    def login_with_google_token(self) -> None:
        """
        Launches a real Chrome window for the user to complete Google OAuth (email/password/2FA).
        Once redirected back to CRS, it harvests cookies into requests.Session.
        """

        # 1) Fetch the CRS CSRF token
        resp = self.session.get(f"{self.login_url.rstrip('/')}/login")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrf_token"})
        csrf = csrf_input.get("value", "") if isinstance(csrf_input, Tag) else ""
        if not csrf:
            raise RuntimeError("Could not find CRS CSRF token")

        # 2) Initiate the Google-OAuth handshake (this assumes Google authentication is done, and email is known)
        oauth_resp = self.session.post(
            f"{self.login_url.rstrip('/')}/auth/login_upmail",
            data={"csrf_token": csrf},
            allow_redirects=False,
        )
        oauth_resp.raise_for_status()
        google_url = oauth_resp.headers.get("Location")
        if not google_url:
            raise RuntimeError("No Google redirect URL in OAuth response")

        # 3) Launch Chrome for manual login (no need for manual input, as the credentials are already obtained)
        options = Options()
        # Remove headless: user will see and interact
        # options.binary_location = "/usr/bin/chromium"
        # options.add_argument("--headless=new")          # or "--headless"
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-gpu")            # if you hit GPU errors
        # isolate profile to avoid conflicts
        profile_dir = tempfile.mkdtemp(prefix=f"chrome-{uuid.uuid4().hex}-")
        options.add_argument(f"--user-data-dir={profile_dir}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        try:
            # Open the OAuth URL; user will enter Google credentials and 2FA manually (if not handled yet)
            driver.get(google_url)

            # Wait until CRS domain is loaded again after Google completes login
            WebDriverWait(driver, 300).until(EC.url_contains("crs.upd.edu.ph"))

            # Now explicitly fetch the protected page so CRS will issue
            # its session cookie(s):
            driver.get(f"{self.login_url.rstrip('/')}/user/view/classmessages")
            # wait for something unique on that page, e.g. the registration_details table
            WebDriverWait(driver, 300).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table#registration_details"))
            )

        finally:
            # Harvest cookies back into requests.Session
            cookies = driver.get_cookies()
            self._selenium_cookies = cookies[:]  
            for c in cookies:
                self.session.cookies.set(
                    c["name"],
                    c["value"],
                    domain=c.get("domain"),
                    path=c.get("path"),
                    secure=c.get("secure", False),
                    rest={"HttpOnly": c.get("httpOnly", False)}
                )
            driver.quit()

    def get_priority(self) -> None:
        # Scrape the preenlistment priority in the homepage
        response = self.session.get(self.homepage_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.select_one("html body div#content div#rightcolumn table#registration_details")

        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td") if isinstance(row, Tag) else []
                if cells:
                    if "Preenlistment Priority" in cells[0].get_text(separator="\n", strip=True):
                        self.preenlistment_priority = cells[1].get_text(separator="\n", strip=True)
                    elif "Registration Priority" in cells[0].get_text(separator="\n", strip=True):
                        self.registration_priority = cells[1].get_text(separator="\n", strip=True)

        print(f"Preenlistment Priority: {self.preenlistment_priority}")
        print(f"Registration Priority: {self.registration_priority}")

    def access_all_possible_course_schedules(self) -> None:
        if self.all_course_table_schedule_url != ['']:
            for course_url in self.all_course_table_schedule_url:
                print(f"Accessing {course_url}...")
                response = self.session.get(course_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.select_one("html body div#content div#rightcolumn table#tbl-search")

                if table:
                    for row in table.find_all("tr")[1:]:
                        if not isinstance(row, Tag):
                            continue
                        no_matching = row.get_text(separator="\n", strip=True)

                        if no_matching == "No matching results":
                            raise ValueError("No matching results found or invalid course URL")

                        cells = row.find_all("td") if isinstance(row, Tag) else []
                        if cells:
                            self.append_sorted_row_data(cells)
        else:
            raise ValueError("No course URLs provided")

    def append_sorted_row_data(self, cells: list[Tag]) -> None:
        course, section = self.extract_course_and_section(cells[1].get_text(separator="\n", strip=True).split('\n'))
        formatted_schedule = self.format_schedule(cells)

        course_entry = next((subject for subject in self.data if course in subject), None)

        if course_entry:
            course_entry[course].append({section: formatted_schedule})
        else:
            self.data.append({course: [{section: formatted_schedule}]})

    def extract_course_and_section(self, class_info: list[str]) -> tuple[str, str]:
        class_name = class_info[0].split(" ")
        return f"{class_name[0]} {class_name[1]}", class_name[2]

    def format_schedule(self, cells: list[Tag]) -> Schedule:
        schedule_parts = cells[3].get_text(separator="\n", strip=True).split('\n')
        schedule = schedule_parts[0].split('; ') if len(schedule_parts) == 1 else schedule_parts
        available_total_slots = cells[5].get_text(separator="\n", strip=True).replace('\xa0', '').replace('\n', '')
        demand = int(cells[6].get_text(separator="\n", strip=True).replace('\xa0', ''))
        credits = cells[2].get_text(separator="\n", strip=True).split('\n')
        available_slots = int(available_total_slots.split("/")[0])

        return [
            {
                "Day": sched.split(" ")[0],
                "Time": sched.split(" ")[1],
                "Room": sched.split(" ")[2] if len(sched.split(" ")) > 2 else "",
                "Available Slots": available_slots,
                "Total Slots": int(available_total_slots.split("/")[1]),
                "Demand": int(demand),
                "Credits": sum([float(credit.strip('()')) for credit in credits]),
                "Probability": round(self.probability_calculator.calculate_probability(self.preenlistment_priority.lower(), available_slots, int(demand), True), 4) * 100,
                "Instructors": cells[1].get_text(separator=", ", strip=True).split(', ')[1],
            } for sched in schedule
        ]