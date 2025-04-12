def satisfies_prerequisites(course, assignment, course_term, prerequisites):
    """
    Recursively check prerequisites. If a prerequisite is scheduled but not yet assigned,
    we defer the check (assume it can be satisfied later).
    """
    term_order = {"Completed": -1, "Term1": 0, "Term2": 1}
    
    if course in course_term and course_term[course] == "Completed":
        return True
    if course not in course_term:
        return True
    if course not in prerequisites:
        return True
    if course not in assignment:
        return True  
    course_term_val = assignment[course][0]
    for req in prerequisites[course]:
        if isinstance(req, (list, tuple)):
            group_satisfied = False
            for alt in req:
                if alt in course_term and course_term[alt] == "Completed":
                    group_satisfied = True
                    break
                if alt not in assignment:
                    group_satisfied = True  
                    break
                alt_term = assignment[alt][0]
                if term_order[alt_term] < term_order[course_term_val]:
                    if satisfies_prerequisites(alt, assignment, course_term, prerequisites):
                        group_satisfied = True
                        break
            if not group_satisfied:
                return False
        else:
            if req in course_term and course_term[req] == "Completed":
                continue
            if req not in assignment:
                continue  
            req_term = assignment[req][0]
            if term_order[req_term] >= term_order[course_term_val]:
                return False
            if not satisfies_prerequisites(req, assignment, course_term, prerequisites):
                return False
    return True

def prerequisite_constraint_transitive(var, value, assignment, course_term, prerequisites):
    """
    Check that the full chain of prerequisites for course `var` is satisfied.
    When a prerequisite is not yet assigned, the check is deferred.
    """
    term_order = {"Completed": -1, "Term1": 0, "Term2": 1}
    course_term_val = value[0]
    if var in course_term and course_term[var] == "Completed":
        return True
    if var not in prerequisites:
        return True
    for req in prerequisites[var]:
        if isinstance(req, (list, tuple)):
            group_satisfied = False
            for alt in req:
                if alt in course_term and course_term[alt] == "Completed":
                    group_satisfied = True
                    break
                if alt not in course_term:
                    group_satisfied = True
                    break
                if alt not in assignment:
                    group_satisfied = True  
                    break
                alt_term = assignment[alt][0]
                if term_order[alt_term] < term_order[course_term_val]:
                    if satisfies_prerequisites(alt, assignment, course_term, prerequisites):
                        group_satisfied = True
                        break
            if not group_satisfied:
                return False
        else:
            if req in course_term and course_term[req] == "Completed":
                continue
            if req not in course_term:
                continue
            if req not in assignment:
                continue  
            req_term = assignment[req][0]
            if term_order[req_term] >= term_order[course_term_val]:
                return False
            if not satisfies_prerequisites(req, assignment, course_term, prerequisites):
                return False
    return True

def generic_constraint(var, value, assignment, course_term, prerequisites):
    return prerequisite_constraint_transitive(var, value, assignment, course_term, prerequisites)

def professor_availability_constraint(var, value, assignment, course_term, prerequisites):
    term, slot, time_label, building, room, professor = value
    availability = {
        "Johnson": {
            "Term1": ["10AM", "11AM"],
            "Term2": ["9AM", "2PM"]
        },
        "Smith": {
            "Term1": ["8AM", "9AM"],
            "Term2": ["9AM", "10AM", "11AM"]
        },
        "Williams": {
            "Term1": ["11AM", "1PM", "3PM"],
            "Term2": ["11AM", "12PM", "2PM"]
        },
        "Brown": {
            "Term1": ["8AM", "9AM", "10AM", "1PM"],
            "Term2": ["10AM", "12PM", "2PM", "3PM"]
        },
        "Anderson": {
            "Term1": ["8AM", "9AM", "10AM", "11AM", "1PM"],
            "Term2": ["8AM", "9AM", "10AM", "11AM", "1PM"]
        },
        "Taylor": {
            "Term1": ["9AM", "11AM", "1PM", "3PM"],
            "Term2": ["10AM", "12PM", "2PM", "4PM"]
        }
    }
    
    if professor in availability and term in availability[professor]:
        return time_label in availability[professor][term]
    return True

def professor_specialty_constraint(var, value, assignment, course_term, prerequisites):
    professor_specialties = {
        "Johnson": ["PHYS", "CHEM"],
        "Smith": ["MATH", "CMPUT"],
        "Williams": ["CMPUT", "STAT"],
        "Brown": ["ENGL", "HIST"],
        "Anderson": ["PSYCO", "ECON"],
        "Taylor": ["BIOL", "ANTHRO", "ENGL"]
    }
    _, _, _, _, _, professor = value
    allowed_prefixes = professor_specialties.get(professor, [])
    if not allowed_prefixes:
        return True
    return any(var.startswith(prefix) for prefix in allowed_prefixes)

def room_capacity_constraint(var, value, assignment, course_term, prerequisites):
    def day_type(slot):
        if slot.startswith("MWF"):
            return "MWF"
        elif slot.startswith("TTH"):
            return "TTH"
        else:
            return None

    capacity_tracker = {}
    temp_assignment = assignment.copy()
    temp_assignment[var] = value

    for course, assign_val in temp_assignment.items():
        term, slot, time_label, building, room, professor = assign_val
        d_type = day_type(slot)
        key = (term, building, room, d_type)
        capacity_tracker[key] = capacity_tracker.get(key, 0) + 1
        if capacity_tracker[key] > 2:
            return False
    return True

def room_diversity_constraint(var, value, assignment, course_term, prerequisites):
    term, slot, time_label, building, room, professor = value
    room_count = 0
    for existing_var, existing_val in assignment.items():
        e_term, e_slot, e_time, e_building, e_room, e_prof = existing_val
        if e_term == term and e_building == building and e_room == room:
            room_count += 1
    return room_count < 2

def required_courses_constraint(var, value, assignment, course_term, prerequisites):
    return True
