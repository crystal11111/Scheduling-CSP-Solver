from collections import deque
import time

class CSP:
    def __init__(self, variables, domains, neighbors, constraints=None, prerequisites=None, course_term=None, preferences=None):
        """
        variables: list of course codes.
        domains: dict mapping each variable to a list of possible assignments.
                 Each assignment is a tuple:
                   (term, slot, time_label, building, room, professor)
        neighbors: dict mapping each variable to a list of other variables that may conflict.
        constraints: dict mapping a constraint name to a function of 
                     (var, value, assignment, course_term, prerequisites).
        prerequisites: dict mapping courses to their direct prerequisites.
        course_term: dict mapping each course to its fixed term ("Term1", "Term2", or "Completed")
        preferences: dict mapping preference name to a function that scores assignments
        """
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints if constraints is not None else {}
        self.prerequisites = prerequisites if prerequisites is not None else {}
        self.course_term = course_term
        self.preferences = preferences if preferences is not None else {}
        self.no_goods = set()  # record failed partial assignments

        # Performance metrics.
        self.backtracks = 0
        self.consistency_checks = 0
        self.forward_check_calls = 0

    def is_consistent(self, var, value, assignment):
        self.consistency_checks += 1
        term, slot, time_label, building, room, professor = value

        # Check all already-assigned neighbors (enforcing an all-different on slots within the term)
        for neighbor in self.neighbors.get(var, []):
            if neighbor in assignment:
                n_term, n_slot, n_time, n_building, n_room, n_professor = assignment[neighbor]
                if term == n_term and slot == n_slot:
                    return False

        # Check custom constraints.
        for cname, constraint in self.constraints.items():
            if not constraint(var, value, assignment, self.course_term, self.prerequisites):
                return False
        return True

    def select_unassigned_variable(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        # MRV heuristic; tie-breaker uses the degree heuristic.
        return min(unassigned,
                   key=lambda var: (len(self.domains[var]),
                                    -len([n for n in self.neighbors.get(var, []) if n not in assignment])))

    def order_domain_values(self, var, assignment, domains):
        def calculate_value_score(value):
            term, slot, time_label, building, room, professor = value
            conflict_count = 0
            for neighbor in self.neighbors.get(var, []):
                for neighbor_val in domains[neighbor]:
                    if term == neighbor_val[0] and slot == neighbor_val[1]:
                        conflict_count += 1

            preference_score = 0
            for pref_name, pref_func in self.preferences.items():
                preference_score += pref_func(var, value, assignment)
            
            # A higher score is better, so subtract conflicts.
            return preference_score - conflict_count

        return sorted(domains[var], key=lambda val: calculate_value_score(val), reverse=True)

    def forward_checking(self, var, value, assignment, local_domains):
        self.forward_check_calls += 1
        term, slot, time_label, building, room, professor = value

        for neighbor in self.neighbors.get(var, []):
            if neighbor not in assignment:
                new_domain = []
                for val in local_domains[neighbor]:
                    n_term, n_slot, n_time, n_building, n_room, n_professor = val
                    if term == n_term and slot == n_slot:
                        continue  # Conflict: same term and same slot
                    new_domain.append(val)
                local_domains[neighbor] = new_domain
                if not local_domains[neighbor]:
                    return False
        return True

    def revise(self, domains, xi, xj):
        revised = False
        to_remove = []
        # Enforce two conditions:
        # 1. If values share the same term, they cannot have the same slot.
        # 2. Lexicographic ordering: if xi < xj and same term, then slot number for xi must be less than xj.
        for x in domains[xi]:
            def compatible(x, y):
                if x[0] == y[0] and x[1] == y[1]:
                    return False
                if xi < xj and x[0] == y[0]:
                    try:
                        x_slot = int(x[1][3:])
                        y_slot = int(y[1][3:])
                    except Exception:
                        return True
                    if not (x_slot < y_slot):
                        return False
                return True
            if not any(compatible(x, y) for y in domains[xj]):
                to_remove.append(x)
                revised = True
        for x in to_remove:
            domains[xi].remove(x)
        if revised:
            print(f"Revise: For {xi}, removed {len(to_remove)} values; new domain size: {len(domains[xi])}")
        return revised

    def ac3(self, domains):
        queue = deque([(xi, xj) for xi in self.variables for xj in self.neighbors.get(xi, [])])
        print("AC3: Initial queue size:", len(queue))
        while queue:
            xi, xj = queue.popleft()
            old_size = len(domains[xi])
            if self.revise(domains, xi, xj):
                new_size = len(domains[xi])
                print(f"AC3: Revised {xi} due to {xj} (domain size {old_size} -> {new_size})")
                if new_size == 0:
                    print(f"AC3: Domain for {xi} is empty. Inconsistency detected.")
                    return False
                for xk in self.neighbors.get(xi, []):
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def backtrack(self, assignment, domains):
        if len(assignment) == len(self.variables):
            return assignment
        key = frozenset(assignment.items())
        if key in self.no_goods:
            return None
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment, domains):
            if self.is_consistent(var, value, assignment):
                local_domains = {v: list(domains[v]) for v in domains}
                assignment[var] = value
                if self.forward_checking(var, value, assignment, local_domains):
                    result = self.backtrack(assignment, local_domains)
                    if result is not None:
                        return result
                del assignment[var]
                self.backtracks += 1
        self.no_goods.add(key)
        return None

    def solve(self):
        print("Starting to solve...")
        start_time = time.time()
        local_domains = {v: list(self.domains[v]) for v in self.domains}
        print("Initial domain sizes: min=%d, max=%d, avg=%.1f" %
              (min(len(d) for d in local_domains.values()),
               max(len(d) for d in local_domains.values()),
               sum(len(d) for d in local_domains.values()) / len(local_domains)))
        print("Running AC3 for initial constraint propagation...")
        if not self.ac3(local_domains):
            print("Problem is unsolvable after AC3 propagation.")
            return None, {"backtracks": self.backtracks,
                          "consistency_checks": self.consistency_checks,
                          "forward_check_calls": self.forward_check_calls}
        print("Domain sizes after AC3: min=%d, max=%d, avg=%.1f" %
              (min(len(d) for d in local_domains.values()),
               max(len(d) for d in local_domains.values()),
               sum(len(d) for d in local_domains.values()) / len(local_domains)))
        print("Starting backtracking search...")
        solution = self.backtrack({}, local_domains)
        end_time = time.time()
        metrics = {
            "backtracks": self.backtracks,
            "consistency_checks": self.consistency_checks,
            "forward_check_calls": self.forward_check_calls,
            "time_taken": end_time - start_time
        }
        return solution, metrics
