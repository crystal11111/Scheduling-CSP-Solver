def prefer_later_start_times(var, value, assignment):
    _, _, time_label, _, _, _ = value
    time_preference_scores = {
        "8AM": 0,
        "9AM": 1,
        "10AM": 2,
        "11AM": 3,
        "12PM": 4,
        "1PM": 5,
        "2PM": 6,
        "3PM": 7,
        "4PM": 8,
    }
    score = time_preference_scores.get(time_label, 0)
    if time_label in ["11AM", "12PM", "1PM", "2PM", "3PM", "4PM"]:
        score += 2
    return score

def prefer_professor(var, value, assignment):
    _, _, _, _, _, professor = value
    professor_scores = {
        "Anderson": 3,
        "Taylor": 2,
        "Williams": 2,
        "Johnson": 1,
        "Smith": 1,
        "Brown": 0
    }
    return professor_scores.get(professor, 0)

def prefer_building_room(var, value, assignment):
    _, _, _, building, room, _ = value
    building_scores = {
        "CCIS": 2,
        "ETLC": 1,
        "CSC": 2,
        "SUB": 0
    }
    room_scores = {
        "101": 1,
        "201": 1
    }
    return building_scores.get(building, 0) + room_scores.get(room, 0)

def prefer_room_diversity(var, value, assignment):
    _, _, _, building, room, _ = value
    room_uses = 0
    for _, existing_val in assignment.items():
        _, _, _, e_building, e_room, _ = existing_val
        if e_building == building and e_room == room:
            room_uses += 1
    return -1 * room_uses
