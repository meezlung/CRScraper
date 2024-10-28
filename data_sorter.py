from typing import TypeAlias
from crs_data import Data

from datetime import datetime
import json

data_class = Data()

data: list[dict[str, str | list[str]]] = data_class.data() # These are just temporary just for now

Course: TypeAlias = str
Section: TypeAlias = str
Schedule: TypeAlias = list[dict[str, str]]

class DataSorter:
    def __init__(self, data: list[dict[str, str | list[str]]]) -> None:
        data_class = Data()
        self.data = data_class.data()
        self.subjects_with_time: list[dict[Course, list[dict[Section, Schedule]]]] = []

    def sort_data(self) -> None:
        for d in data:

            # Format the class name / instructor(s)
            class_name = d["Class Name / Instructor(s)"][0].split(" ")
            course = class_name[0] + " " + class_name[1]
            section = class_name[2]

            formatted_schedule: list[dict[str, str]] = []

            # Format the schedule / room
            for i in range(len(d["Schedule / Room"])):
                schedule = d["Schedule / Room"][i].split(" ")

                formatted_schedule.append({
                    "Day": schedule[0],
                    "Time": schedule[1],
                    "Room": schedule[2] + " " + schedule[3],
                    # Add more details here if needed, especially for the number of slots available. We need to run some analysis on that too
                })

            # Checks everytime if the course is already in the subjects_with_time list
            if any(course in subject for subject in self.subjects_with_time): 
                for subject in self.subjects_with_time:
                    if course in subject:
                        subject[course].append({
                            section: formatted_schedule
                        })
            else:
                self.subjects_with_time.append({
                    course: [{
                        section: formatted_schedule
                    }]
                })

    def display_data(self, subjects_with_time: list[dict[Course, list[dict[Section, Schedule]]]]) -> None:
        for subject in subjects_with_time:
            print(json.dumps(subject, indent=2))


class ScheduleGenerator:
    def __init__(self, subjects_with_time: list[dict[Course, list[dict[Section, Schedule]]]]) -> None:
        self.subjects_with_time = subjects_with_time
        self.optimized_schedule = []

        self.days_mapping = {
            "M": ["Monday"],
            "T": ["Tuesday"],
            "W": ["Wednesday"],
            "Th": ["Thursday"],
            "F": ["Friday"],
            "S": ["Saturday"],
            "Su": ["Sunday"],
            "MWF": ["Monday", "Wednesday", "Friday"],
            "TTh": ["Tuesday", "Thursday"],
            "WF": ["Wednesday", "Friday"],
            "TF": ["Tuesday", "Friday"],
        }

    def parse_time(self, time: str) -> datetime:
        # If minutes are not provided, append ":00" to the time
        if ':' not in time:
            time += ":00"
        
        # Ensure AM/PM is present, default to AM if not specified
        if 'AM' not in time and 'PM' not in time:
            time += "AM" if int(time.split(':')[0]) < 12 else "PM"
        
        return datetime.strptime(time.strip(), "%I:%M%p").replace(year=2024) # Still need to generalize this

    def parse_days(self, days: str) -> list[str]:
        return self.days_mapping[days] # We need to generalize the code for this because there will be more possible day combinations

    def check_conflict(self, schedule1: Schedule, schedule2: Schedule) -> bool: # Still need to test this
        day1 = schedule1[0]['Day']
        time1 = schedule1[0]['Time']
        
        day2 = schedule2[0]['Day']
        time2 = schedule2[0]['Time']

        # Parse days
        days1 = self.parse_days(day1)
        days2 = self.parse_days(day2)

        # Check if any day overlaps
        overlapping_days = set(days1) & set(days2)
        if not overlapping_days:
            return False  # No conflict if there are no overlapping days

        # Parse times
        start1, end1 = map(self.parse_time, time1.split('-'))
        start2, end2 = map(self.parse_time, time2.split('-'))

        # Check if times overlap
        times_overlap = start1 < end2 and start2 < end1

        return times_overlap if overlapping_days else False
    
    def generate_schedules(self, subjects_with_time: list[dict[Course, list[dict[Section, Schedule]]]], current_schedule: list[dict[Course, Section]], index: int = 0) -> list[list[dict[Course, Section]]]:
        ...