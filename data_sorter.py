from typing import TypeAlias
from crs_data import Data

from datetime import datetime
import json

data_class = Data()

data: list[dict[str, str | list[str]]] = data_class.data() # These are just temporary just for now

Course: TypeAlias = str
Section: TypeAlias = str
Schedule: TypeAlias = list[dict[str, str | int | float]]
ListOfCoursesWithTime: TypeAlias = list[dict[Course, list[dict[Section, Schedule]]]]

class DataSorter:
    def __init__(self, data: list[dict[str, str | list[str]]]) -> None:
        data_class = Data()
        self.data = data_class.data()
        self.subjects_with_time: ListOfCoursesWithTime = []

    def sort_data(self) -> None:
        for d in data:

            # Format the class name / instructor(s)
            class_name = d["Class Name / Instructor(s)"][0].split(" ")
            course = class_name[0] + " " + class_name[1]
            section = class_name[2]

            formatted_schedule: Schedule = []

            # Format the schedule / room
            for i in range(len(d["Schedule / Room"])):
                schedule = d["Schedule / Room"][i].split(" ")

                formatted_schedule.append({
                    "Day": schedule[0],
                    "Time": schedule[1],
                    "Room": schedule[2] + " " + schedule[3],
                    "Available Slots": int(str(d["Available Slots / Total Slots"]).split("/")[0]),
                    "Total Slots": int(str(d["Available Slots / Total Slots"]).split("/")[1]),
                    "Demand": int(str(d["Demand"])),
                    "Credits": float(d["Credits"][0]) + float(d["Credits"][1]) if len(d["Credits"]) > 1 else float(d["Credits"][0]),
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

    def display_data(self, subjects_with_time: ListOfCoursesWithTime) -> None:
        for subject in subjects_with_time:
            print(json.dumps(subject, indent=2))


class ScheduleGenerator:
    def __init__(self, subjects_with_time: ListOfCoursesWithTime) -> None:
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

    def parse_time(self, time: str) -> tuple[datetime, datetime]:
        start_time, end_time = time.split('-')

        # Check if AM is specified only in the end time and not in the start time
        if 'AM' in end_time or 'PM' in end_time:

            # If end_time has AM/PM but start_time doesn't, append the same AM/PM to start_time
            if 'AM' not in start_time and 'PM' not in start_time:

                # Append ":00" to the times if minutes are not provided
                if ':' not in start_time:
                    start_time += ":00"
                if ':' not in end_time:
                    end_time = end_time[:-2] + ":00" + end_time[-2:]

                start_time += end_time[-2:] # Add 'AM' or 'PM' from end_time to start_time


            # Cases where the time range spans noon (e.g. 11AM-1PM)
            elif 'AM' in start_time and 'PM' in end_time:
                if ':' not in start_time:
                    start_time = start_time[:-2] + ":00" + start_time[-2:]            
                if ':' not in end_time:
                    end_time = end_time[:-2] + ":00" + end_time[-2:]

        

            # Cases where the time range spans midnight (e.g. 11PM-1AM) - Most Unlikely
            elif 'PM' in start_time and 'AM' in end_time:
                if ':' not in start_time:
                    start_time = start_time[:-2] + ":00" + start_time[-2:]            
                if ':' not in end_time:
                    end_time = end_time[:-2] + ":00" + end_time[-2:]


        # Parse both times as datetime objects
        start_time = datetime.strptime(start_time.strip(), "%I:%M%p").replace(year=2024)
        end_time = datetime.strptime(end_time.strip(), "%I:%M%p").replace(year=2024)

        return start_time, end_time

    def parse_days(self, days: str) -> list[str]:
        return self.days_mapping[days] # We need to generalize the code for this because there will be more possible day combinations

    def check_conflict(self, accumulated_schedule: list[Schedule], new_schedule: Schedule) -> bool: # Still need to test this

        for existing_schedule in accumulated_schedule:
            for entry1 in existing_schedule:
                for entry2 in new_schedule:
                    
                    if type(entry1["Day"]) == str and type(entry2["Day"]) == str:
                        # Parse the days and check for any overlap
                        days1 = self.parse_days(entry1["Day"])
                        days2 = self.parse_days(entry2["Day"])
                        overlapping_days = set(days1) & set(days2)
                    
                        if overlapping_days:
                            if type(entry1["Time"]) == str and type(entry2["Time"]) == str:    
                                # Parse the time and check for any overlap
                                start1, end1 = self.parse_time(entry1["Time"])
                                start2, end2 = self.parse_time(entry2["Time"])

                                if start1 < end2 and start2 < end1:
                                    return True
        
        return False

    def backtrack(self, subjects_with_time: ListOfCoursesWithTime, 
                        current_index: int, 
                        current_schedule: ListOfCoursesWithTime, 
                        all_schedules: list[ListOfCoursesWithTime], 
                        accumulated_schedule: list[Schedule]) -> None:
        

        if current_index == len(subjects_with_time):
            all_schedules.append(current_schedule.copy())
            return
        
        subject_with_time = subjects_with_time[current_index]
        subject = list(subject_with_time.keys())[0]
        sections = subject_with_time[subject]

        for section_data in sections:
            section = list(section_data.keys())[0]
            schedule = section_data[section]

            if not self.check_conflict(accumulated_schedule, schedule):
                # Choose: Add the schedule to the current schedule
                current_schedule.append({
                    subject: [{section: schedule}]
                })
                accumulated_schedule.append(schedule)

                # Explore: Move on to the next subject
                self.backtrack(subjects_with_time, current_index + 1, current_schedule, all_schedules, accumulated_schedule)

                # Unchoose: Remove the last added section to wbacktrack
                current_schedule.pop()
                accumulated_schedule.pop()

    def generate_schedules(self, subjects_with_time: ListOfCoursesWithTime) -> list[ListOfCoursesWithTime]:
        all_schedules: list[ListOfCoursesWithTime] = []
        self.backtrack(subjects_with_time, 0, [], all_schedules, [])
        return all_schedules

    def display_all_possible_schedules(self, all_schedules: list[ListOfCoursesWithTime]) -> None:
        for schedule in all_schedules:
            print(json.dumps(schedule, indent=2))
            print("\n" + "-" * 40 + "\n")
