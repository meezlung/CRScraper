# This is highly inspired by Leonard Ang's code in his UPD-Course-Probability-Calculator (https://github.com/drew-747/UPD-Course-Probability-Calculator/blob/main/popup.js)

class ProbabilityCalculator:
    def __init__(self) -> None:
       # Priority to percentage mapping
        self.CUMULATIVE_PRIO_TO_PERCENTAGE_MAP = {
            "specialNeeds": 0.0,
            "graduating": 0.05,
            "assistant": 0.15,
            "freshman": 0.16,
            "varsity": 0.41,
            "cadetOfficer": 0.46,
            "regular": 0.47,
            "lowPriority": 0.95,
        } 

    def get_previous_priority(self, priority: str) -> str:
        # Get the list of priorities in order and find the previous priority
        priorities = list(self.CUMULATIVE_PRIO_TO_PERCENTAGE_MAP.keys())
        index = priorities.index(priority)
        return priorities[index - 1] if index > 0 else ""

    def calculate_probability(self, student_priority: str, available_slots: int, total_demand: int, has_students_with_priority: bool) -> float:
        if available_slots <= 0 or total_demand <= 0:
            return -1.0

        if has_students_with_priority:
            cumulative_percentage = self.CUMULATIVE_PRIO_TO_PERCENTAGE_MAP[student_priority]
            previous_priority = self.get_previous_priority(student_priority)
            previous_cumulative_percentage = self.CUMULATIVE_PRIO_TO_PERCENTAGE_MAP.get(previous_priority, 0)
            
            demand_for_this_priority = total_demand * (cumulative_percentage - previous_cumulative_percentage)
            total_demand_of_higher_prio = total_demand * cumulative_percentage

            if available_slots > total_demand_of_higher_prio:
                return 1.0  # 100% chance if there are more slots than higher priority demand
            else:
                slots_for_this_priority = max(available_slots - (total_demand_of_higher_prio - demand_for_this_priority), 0)
                return slots_for_this_priority / demand_for_this_priority if demand_for_this_priority > 0 else 0
        else:
            return min(available_slots / total_demand, 1.0)

# def main():
#     # Simulate form input
#     available_slots = int(input("Enter available slots: "))
#     total_demand = int(input("Enter total demand: "))
#     student_priority = input("Enter student priority (e.g., 'regular', 'freshman'): ")
#     has_students_with_priority = input("Are there students with priority? (yes/no): ").strip().lower() == 'yes'

#     # Validate inputs
#     if available_slots <= 0 or total_demand <= 0:
#         print("Please enter valid positive numbers for all fields.")
#         return

#     # Calculate probability
#     calculator = ProbabilityCalculator()
#     probability = calculator.calculate_probability(student_priority, available_slots, total_demand, has_students_with_priority)
#     print(f"Probability of getting a slot: {probability * 100:.2f}%")

# if __name__ == "__main__":
#     main()
