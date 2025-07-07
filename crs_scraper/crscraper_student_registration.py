import requests
from bs4 import BeautifulSoup

from bs4.element import Tag
from typing import Optional, Union

class CRScraperStudentRegistration:
    def __init__(self, login_url: str, username: str, password: str, all_course_table_schedule_url: list[str]) -> None:
        self.username = username
        self.password = password

        self.login_url = login_url
        self.all_course_table_schedule_url = all_course_table_schedule_url

        # Start a session
        self.session = requests.Session()
        self.data: list[dict[str, str | list[str]]] = []

    def main(self) -> Optional[list[dict[str, str | list[str]]]]:
        self.login_into_crs()
        data = self.access_all_possible_course_schedules()

        return data

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

    def access_all_possible_course_schedules(self) -> Optional[list[dict[str, str | list[str]]]]:
        if self.all_course_table_schedule_url:
            for course_url in self.all_course_table_schedule_url:
                # Access the page
                response = self.session.get(course_url)
                response.raise_for_status() # Ensure the login was successful

                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                table: Optional[Tag] = soup.select_one("html body div#content div#rightcolumn table#tbl-search")

                # Check if the table exists
                if table:
                    # Iterate over each row in the table body
                    for row in table.find_all("tr")[1:]:  # Skip the header row
                        if not isinstance(row, Tag):
                            continue
                        cells: list[Tag] = [cell for cell in row.find_all("td") if isinstance(cell, Tag)]
                        
                        if len(cells) > 0:

                            class_code: str | list[str] = cells[0].get_text(separator="\n", strip=True).split('\n')

                            class_name_and_instructors: str | list[str] = cells[1].get_text(separator="\n", strip=True).split('\n')
                            credits: str | list[str] = cells[2].get_text(separator="\n", strip=True).split('\n')
                            schedule: str | list[str] = cells[3].get_text(separator="\n", strip=True).split('\n')

                            # Edge case for when there's a weird schedule (i.e. Math 23 and Physics 72)
                            if len(schedule) == 1:
                                schedule = schedule[0].split('; ')

                            waitlisting_schedule: str | list[str] = cells[4].get_text(separator="\n", strip=True).split('\n')
                            restrictions_remarks: str | list[str] = cells[5].get_text(separator="\n", strip=True).split('\n')

                            available_total_slots_raw: str = cells[6].get_text(separator="\n", strip=True)
                            demand_raw: str = cells[7].get_text(separator="\n", strip=True)
                            
                            available_total_slots: str = available_total_slots_raw.replace('\xa0', '').replace('\n', '')
                            demand: str = demand_raw.replace('\xa0', '')

                            # status: str = cells[8].get_text(separator="\n", strip=True)

                            # Store the scraped data in a dictionary
                            row_data: dict[str, str | list[str]] = {
                                "Class Code": class_code,
                                "Class Name / Instructor(s)": class_name_and_instructors,
                                "Credits": credits,
                                "Schedule / Room": schedule,
                                "Waitlisting Schedule": waitlisting_schedule,
                                "Restrictions / Remarks": restrictions_remarks,
                                "Available Slots / Total Slots": available_total_slots, 
                                "Demand": demand,
                                # "Status": status
                            }
                            
                            self.data.append(row_data)

            return self.data
        
        else:
            raise ValueError("No course URLs provided")
            return None
    
    def print_data(self, data: list[dict[str, str | list[str]]] | None) -> None:
        if data:
            for entry in data:
                for key, value in entry.items():
                    print(f'{key}: {value}')
                print("\n" + "-" * 40 + "\n")

