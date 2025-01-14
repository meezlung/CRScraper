import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Optional, Union
from crs_scraper.probability_calculator import ProbabilityCalculator

Course = str
Section = str
Schedule = list[dict[str, str | int | float]]
ListOfCoursesWithTime = list[dict[Course, list[dict[Section, Schedule]]]]

class CRScraperStudentRegistration:
    def __init__(self, login_url: str, username: str, password: str, all_course_table_schedule_url: list[str]) -> None:
        self.username = username
        self.password = password
        self.login_url = login_url
        self.all_course_table_schedule_url = all_course_table_schedule_url

        # Start a session
        self.session = requests.Session()
        self.data: ListOfCoursesWithTime = []  # Now in sorted format directly
        self.probability_calculator = ProbabilityCalculator()

    def main(self) -> Optional[ListOfCoursesWithTime]:
        print("Logging into CRS...")
        self.login_into_crs()
        print("Logged in successf4ully.")
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
                        no_matching = row.get_text(separator="\n", strip=True)

                        if no_matching == "No matching results":
                            raise ValueError("No matching results found or invalid course URL")

                        cells = row.find_all("td")
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
        available_total_slots = cells[6].get_text(separator="\n", strip=True).replace('\xa0', '').replace('\n', '')
        demand = int(cells[7].get_text(separator="\n", strip=True).replace('\xa0', ''))
        credits = cells[2].get_text(separator="\n", strip=True).split('\n')
        available_slots = int(available_total_slots.split("/")[0])

        waitlisting_schedule = cells[4].get_text(separator="\n", strip=True).split('\n')
        action = cells[8].get_text(separator="\n", strip=True).split('\n')

        probability = 0.0

        if waitlisting_schedule[0].upper() == "CLOSED" and action[0].upper() == "ENLISTED ALREADY": # If you already got the subject in preenlistment
            probability = 100.0

        elif waitlisting_schedule[0].upper() == "CLOSED" or action[0].upper() == "CLOSED": # If subject is closed
            probability = -100.0

        else: # If the subject is open
            probability = round(self.probability_calculator.calculate_probability("regular", available_slots, int(demand), True), 4) * 100

        return [
            {
                "Day": sched.split(" ")[0],
                "Time": sched.split(" ")[1],
                "Room": sched.split(" ")[2] if len(sched.split(" ")) > 2 else "",
                "Available Slots": available_slots,
                "Total Slots": int(available_total_slots.split("/")[1]),
                "Demand": int(demand),
                "Credits": sum([float(credit.strip('()')) for credit in credits]),
                "Probability": probability,
                "Instructors": cells[1].get_text(separator=", ", strip=True).split(', ')[1],
            } for sched in schedule
        ]