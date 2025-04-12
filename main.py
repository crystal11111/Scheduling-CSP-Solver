from csp import CSP

from constraints import (
    prerequisite_constraint_transitive,
    professor_availability_constraint,
    professor_specialty_constraint,
    room_capacity_constraint,
    room_diversity_constraint,
    required_courses_constraint
)
from preferences import (
    prefer_later_start_times,
    prefer_professor,
    prefer_building_room,
    prefer_room_diversity
)

def main():
    # 2 academic terms
    terms = ["Term1", "Term2"]

    # define slot types
    MWF_slots = [
        ("MWF1", "8AM"), ("MWF2", "9AM"), ("MWF3", "10AM"),
        ("MWF4", "11AM"), ("MWF5", "12PM"), ("MWF6", "1PM"),
        ("MWF7", "2PM"), ("MWF8", "3PM"), ("MWF9", "4PM")
    ]
    
    TTH_slots = [
        ("TTH1", "8AM"), ("TTH2", "9AM"), ("TTH3", "10AM"),
        ("TTH4", "11AM"), ("TTH5", "12PM"), ("TTH6", "1PM"),
        ("TTH7", "2PM"), ("TTH8", "3PM"), ("TTH9", "4PM")
    ]

    buildings = ["CCIS", "ETLC", "CSC", "SUB"]
    rooms = ["101", "201"]
    professors = ["Smith", "Johnson", "Williams", "Brown", "Anderson", "Taylor"]

    # course options for Term1 and Term2
    term1_MWF_course_options = [
        "CMPUT174", "MATH144", "CMPUT204", "PHYS124", "CHEM101",
        "ENGL103", "STAT151", "ECON101", "PSYCO104", "PHIL102"
    ]
    term1_TTH_course_options = [
        "MATH134", "BIOL107", "ENGL102", "HIST116", "ANTHRO101",
        "PSYCO105", "SOC100", "DRAMA102"
    ]
    term2_MWF_course_options = [
        "CMPUT201", "MATH146", "CMPUT366", "PHYS126", "CHEM102",
        "ENGL104", "STAT152", "ECON102", "PSYCO106", "PHIL103"
    ]
    term2_TTH_course_options = [
        "MATH136", "BIOL207", "ENGL103", "HIST117", "ANTHRO201",
        "PSYCO223", "SOC101", "DRAMA202"
    ]

    # deterministically select courses
    term1_MWF_courses = sorted(term1_MWF_course_options)[:3]
    term1_TTH_courses = sorted(term1_TTH_course_options)[:2]
    term2_MWF_courses = sorted(term2_MWF_course_options)[:3]
    term2_TTH_courses = sorted(term2_TTH_course_options)[:2]
    
    term1_courses = term1_MWF_courses + term1_TTH_courses
    term2_courses = term2_MWF_courses + term2_TTH_courses
    variables = term1_courses + term2_courses
    
    print(f"\nSelected Term 1 MWF courses: {term1_MWF_courses}")
    print(f"Selected Term 1 TTH courses: {term1_TTH_courses}")
    print(f"Selected Term 2 MWF courses: {term2_MWF_courses}")
    print(f"Selected Term 2 TTH courses: {term2_TTH_courses}")

    # map each course to its term
    course_term = {}
    for course in term1_courses:
        course_term[course] = "Term1"
    for course in term2_courses:
        course_term[course] = "Term2"
        
    # --- Mark completed courses ---
    completed_courses = {"MATH134"}
    for course in completed_courses:
        course_term[course] = "Completed"
    print("\nCompleted courses:", completed_courses)

    # build domains
    domains = {}
    for course in variables:
        term = course_term[course]
        slots = MWF_slots if (course in term1_MWF_courses or course in term2_MWF_courses) else TTH_slots
        course_values = []
        for slot in slots:
            slot_id, time_label = slot
            for building in buildings:
                for room in rooms:
                    for professor in professors:
                        course_values.append((term, slot_id, time_label, building, room, professor))
        domains[course] = course_values
        print(f"{course}: {len(course_values)} possible assignments")

    # define explicit prerequisites
    prerequisites = {
        "CMPUT204": [["MATH144", "MATH134"]],
        "MATH146": ["MATH144"],
        "BIOL207": ["BIOL107"],
        "MATH136": ["MATH134"],
        "CMPUT366": ["CMPUT204"]
    }
    
    print("\n=== Prerequisites ===")
    for course, reqs in prerequisites.items():
        req_str = []
        for req in reqs:
            if isinstance(req, (list, tuple)):
                req_str.append(" or ".join(req))
            else:
                req_str.append(req)
        print(f"{course} requires: {', '.join(req_str)}")

    # build neighbors
    neighbors = {}
    for course in variables:
        neighbors[course] = set()
    for course in variables:
        for other in variables:
            if other != course and course_term[other] == course_term[course]:
                neighbors[course].add(other)
    # add prerequisite-based neighbor relationships
    for adv, prereq_list in prerequisites.items():
        for prereq in prereq_list:
            if isinstance(prereq, (list, tuple)):
                for alt in prereq:
                    if alt in variables:
                        neighbors.setdefault(adv, set()).add(alt)
                        neighbors.setdefault(alt, set()).add(adv)
            else:
                if prereq in variables:
                    neighbors.setdefault(adv, set()).add(prereq)
                    neighbors.setdefault(prereq, set()).add(adv)
    for course in neighbors:
        neighbors[course] = list(neighbors[course])
        print(f"{course} has {len(neighbors[course])} neighbors.")

    # constraint functions
    constraints = {
        "prerequisite": prerequisite_constraint_transitive,
        "prof_availability": professor_availability_constraint,
        "room_capacity": room_capacity_constraint,
        "room_diversity": room_diversity_constraint,
        "required_courses": required_courses_constraint,
        "prof_specialty": professor_specialty_constraint
    }
    
    # Preference functions
    preferences = {
        "later_start_time": prefer_later_start_times,
        "professor_preference": prefer_professor,
        "building_room_preference": prefer_building_room,
        "room_diversity_preference": prefer_room_diversity
    }

    print("\nCreating and solving the enhanced 2-term scheduling CSP without randomness...")
    scheduling_csp = CSP(variables, domains, neighbors, constraints, prerequisites, course_term, preferences)
    solution, metrics = scheduling_csp.solve()

    if solution:
        print("\n=== Solution Found ===")
        schedule = {"Term1": {"MWF": [], "TTH": []}, "Term2": {"MWF": [], "TTH": []}}
        for course, (term, slot, time_label, building, room, professor) in solution.items():
            slot_type = "MWF" if slot.startswith("MWF") else "TTH"
            schedule[term][slot_type].append((slot, time_label, course, building, room, professor))
        
        for term in terms:
            print(f"\n=== {term} Schedule ===")
            for slot_type in ["MWF", "TTH"]:
                print(f"\n  {slot_type} courses:")
                for assignment in sorted(schedule[term][slot_type], key=lambda x: x[1]):
                    slot, time_label, course, building, room, professor = assignment
                    print(f"    {time_label:4} - {course:8} in {building} Room {room} with Prof. {professor}")
        
        late_morning_count = sum(1 for _, (t, s, time, _, _, _) in solution.items() if time in ["10AM", "11AM"])
        afternoon_count = sum(1 for _, (t, s, time, _, _, _) in solution.items() if time in ["12PM", "1PM", "2PM", "3PM", "4PM"])
        preferred_profs = sum(1 for _, (t, s, time, b, r, prof) in solution.items() if prof in ["Anderson", "Taylor", "Williams"])
        
        room_usage = {}
        for _, (term, _, _, building, room, _) in solution.items():
            key = (term, building, room)
            room_usage[key] = room_usage.get(key, 0) + 1
        
        unique_rooms = len(room_usage)
        max_room_usage = max(room_usage.values()) if room_usage else 0
        
        print("\n=== Schedule Statistics ===")
        print(f"Courses starting at 10AM or 11AM: {late_morning_count}")
        print(f"Afternoon courses (12PM-4PM): {afternoon_count}")
        print(f"Courses with preferred professors: {preferred_profs}")
        print(f"Number of unique room assignments: {unique_rooms}")
        print(f"Maximum number of courses in any room: {max_room_usage}")
        
        print("\n=== Room Usage ===")
        for (term, building, room), count in sorted(room_usage.items()):
            print(f"{term} {building} Room {room}: {count} course(s)")
        
        print("\n=== Performance Metrics ===")
        print(f"Backtracks: {metrics['backtracks']}")
        print(f"Consistency checks: {metrics['consistency_checks']}")
        print(f"Forward checking calls: {metrics['forward_check_calls']}")
        print(f"Time taken: {metrics['time_taken']:.2f} seconds")
    else:
        print("No solution exists with these constraints.")
        print(f"Backtracks: {metrics['backtracks']}")
        print(f"Consistency checks: {metrics['consistency_checks']}")
        print(f"Forward checking calls: {metrics['forward_check_calls']}")

if __name__ == '__main__':
    main()
