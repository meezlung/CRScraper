from typing import TypeAlias
from datetime import datetime
import json
import csv
from probability_calculator import ProbabilityCalculator

Course: TypeAlias = str
Section: TypeAlias = str
Schedule: TypeAlias = list[dict[str, str | int | float]]
ListOfCoursesWithTime: TypeAlias = list[dict[Course, list[dict[Section, Schedule]]]]

class DataSorter:
    def __init__(self, data: list[dict[str, str | list[str]]]) -> None:
        """ Initializes the DataSorter with the provided data. """
        self.data = data
        self.subjects_with_time: ListOfCoursesWithTime = []
        self.ProbabilityCalculator = ProbabilityCalculator()

    def sort_data(self) -> None:
        """ Sorts the data by iterating through each entry in self.data, extracting the course and section
        information, and formatting the schedule. Depending on whether the course already exists, it 
        either adds the section to the existing course or creates a new course entry. """
        for d in self.data:
            course, section = self.extract_course_and_section(d["Class Name / Instructor(s)"])
            formatted_schedule: Schedule = self.format_schedule(d)

            if self.course_exists(course): 
                self.add_section_to_existing_course(course, section, formatted_schedule)

            else:
                self.add_new_course(course, section, formatted_schedule)

    def extract_course_and_section(self, class_info: str | list[str]) -> tuple[str, str]:
        """ Extracts the course name and section from a given class information string or list of strings. 
        Class Info[0] and Class Info[1] are the course name, respectively. Class Info[2] is the section"""
        class_name = class_info[0].split(" ")
        return f"{class_name[0]} {class_name[1]}", class_name[2]
    
    def course_exists(self, course: str) -> bool:
        """ Check if a course exists within the subjects with time. """
        return any(course in subject for subject in self.subjects_with_time)

    def format_schedule(self, d: dict[str, str | list[str]]) -> Schedule:
        """ Formats the schedule by extracting the day, time, room, available slots, total slots, demand, credits, and instructors. """
        formatted_schedule: Schedule = []

        for i in range(len(d["Schedule / Room"])):
            schedule_parts = d["Schedule / Room"][i].split(" ")

            if i == 0:
                formatted_schedule.append({
                    # Essential for comparing conflicts
                    "Day": schedule_parts[0],
                    "Time": schedule_parts[1],

                    # Additional information
                    "Room": f"{schedule_parts[2]} {schedule_parts[3]}",
                    "Available Slots": self.get_available_slots(str(d["Available Slots / Total Slots"])),
                    "Total Slots": self.get_total_slots(str(d["Available Slots / Total Slots"])),
                    "Demand": self.get_demand(str(d["Demand"])),
                    "Credits": self.calculate_total_credits(d["Credits"]),
                    "Probability": round(self.ProbabilityCalculator.calculate_probability("regular", self.get_available_slots(str(d["Available Slots / Total Slots"])), self.get_demand(str(d["Demand"])), True), 4) * 100,
                    "Instructors": self.format_instructions(d["Class Name / Instructor(s)"])[i],
                })
            else:
                formatted_schedule.append({
                    # Essential for comparing conflicts
                    "Day": schedule_parts[0],
                    "Time": schedule_parts[1],

                    # Additional information
                    "Room": f"{schedule_parts[2]} {schedule_parts[3]}",
                    "Available Slots": "",
                    "Total Slots": "",
                    "Demand": "",
                    "Credits": "",
                    "Probability": "",
                    "Instructors": self.format_instructions(d["Class Name / Instructor(s)"])[i],
                })

        return formatted_schedule

    def get_available_slots(self, available_total_slots: str) -> int:
        """ Extracts the available slots from the available total slots string. """
        return int(available_total_slots.split("/")[0])
    
    def get_total_slots(self, available_total_slots: str) -> int:
        """ Extracts the total slots from the available total slots string. """
        return int(available_total_slots.split("/")[1])
    
    def get_demand(self, demand: str) -> int:
        """ Extracts the demand from the demand string. """
        return int(demand)

    def calculate_total_credits(self, credits: str | list[str]) -> float:
        """ Calculates the total credits from the credits string. Credits is a list of strings, usually with 1 or more than 1 element. """
        return sum([float(credit) for credit in credits])

    def format_instructions(self, instructors: str | list[str]) -> str | tuple[str, str]:
        """ Formats the instructors string or list of instructors. """
        return instructors[1], instructors[3] if len(instructors) > 2 else instructors[1]

    def add_section_to_existing_course(self, course: str, section: str, formatted_schedule: Schedule) -> None:
        """ Adds a new section to an existing course. """
        for subject in self.subjects_with_time:
            if course in subject:
                subject[course].append({section: formatted_schedule})

    def add_new_course(self, course: str, section: str, formatted_schedule: Schedule) -> None:
        """ Adds a new course to the subjects with time. """
        self.subjects_with_time.append({course: [{section: formatted_schedule}]})

    def display_data(self, subjects_with_time: ListOfCoursesWithTime) -> None:
        """ Displays the subjects with time in a readable format. """
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
                    
                    if isinstance(entry1["Day"], str) and isinstance(entry2["Day"], str):
                        # Parse the days and check for any overlap
                        days1 = self.parse_days(entry1["Day"])
                        days2 = self.parse_days(entry2["Day"])
                        overlapping_days = set(days1) & set(days2)
                    
                        if overlapping_days:
                            if isinstance(entry1["Time"], str) and isinstance(entry2["Time"], str):    
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
            # print(json.dumps(current_schedule, indent=2))
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

    def convert_to_csv(self, all_schedules: list[ListOfCoursesWithTime], filename: str) -> None:
        headers = [
            "Course", "Section", "Day", "Time", "Room",
            "Available Slots", "Total Slots", "Demand", "Credits", "Probability", "Instructors" 
        ]
        
        with open(filename, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            # Flatten and write each schedule to the CSV
            for schedules in all_schedules:

                # Add an empty row to separate each schedule
                writer.writerow({})

                for course_entry in schedules:
                    for course, sections in course_entry.items():
                        for section_entry in sections:
                            for section, schedule_list in section_entry.items():
                                for schedule in schedule_list:
                                    row: dict[str, Course | int | float] = {
                                        "Course": course,
                                        "Section": section,
                                        **schedule
                                    }
                                    writer.writerow(row)

    def calculate_average_probability(self, schedule: ListOfCoursesWithTime) -> float:
        probabilities: list[float] = []
        for course_entry in schedule:
            for _, sections in course_entry.items():
                for section_entry in sections:
                    for _, schedule_list in section_entry.items():
                        for entry in schedule_list:
                            if "Probability" in entry and isinstance(entry["Probability"], (int, float)):
                                if entry["Probability"]:
                                    probabilities.append(float(entry["Probability"]))
    
        return sum(probabilities) / len(probabilities) if probabilities else 0.0

    def rank_by_probability(self, all_schedules: list[ListOfCoursesWithTime]) -> list[ListOfCoursesWithTime]:
        # Rank schedules by average probability
        all_schedules.sort(
            key=self.calculate_average_probability,
            reverse=True
        )
        
        return all_schedules