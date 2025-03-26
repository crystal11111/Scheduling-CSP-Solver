# A CSP solver for a scheduling problem.
# Each variable represents a course that needs to be scheduled into one of several time slots.
# Conflicts between courses (e.g., sharing the same professor or room) are represented as neighbors,
# meaning those courses cannot be scheduled at the same time.

class CSP:
    def __init__(self, variables, domains, neighbors):
        """
        variables: list of variables (courses).
        domains: dict mapping each variable to a list of possible time slots.
        neighbors: dict mapping each variable to a list of variables that have conflicts with it.
        """
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors

    def is_consistent(self, var, value, assignment):
        """
        Check if assigning value to var is consistent with current assignment.
        For each neighbor of var that has been assigned, ensure no conflict (i.e., same time slot).
        """
        for neighbor in self.neighbors.get(var, []):
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True

    def select_unassigned_variable(self, assignment):
        """
        Select an unassigned variable using the MRV heuristic.
        """
        unassigned = [v for v in self.variables if v not in assignment]
        # Choose the variable with the smallest remaining domain.
        return min(unassigned, key=lambda var: len(self.domains[var]))

    def forward_checking(self, var, value, assignment, local_domains):
        """
        Perform forward checking:
        For each neighbor of var that is not yet assigned, remove the assigned value from its domain.
        Return False if any domain becomes empty (which means a dead end), otherwise True.
        """
        for neighbor in self.neighbors.get(var, []):
            if neighbor not in assignment:
                if value in local_domains[neighbor]:
                    # Remove the conflicting value.
                    local_domains[neighbor] = [v for v in local_domains[neighbor] if v != value]
                    if not local_domains[neighbor]:
                        # If a neighbor has no remaining valid time slots, forward checking fails.
                        return False
        return True

    def backtrack(self, assignment, domains):
        """
        Backtracking search with forward checking.
        """
        # If all variables are assigned, return the assignment.
        if len(assignment) == len(self.variables):
            return assignment

        # Select an unassigned variable using MRV.
        var = self.select_unassigned_variable(assignment)
        for value in domains[var]:
            if self.is_consistent(var, value, assignment):
                # Make a deep copy of domains for forward checking.
                local_domains = {v: list(domains[v]) for v in domains}
                assignment[var] = value
                # Apply forward checking.
                if self.forward_checking(var, value, assignment, local_domains):
                    result = self.backtrack(assignment, local_domains)
                    if result is not None:
                        return result
                # Remove the assignment if it didn't lead to a solution.
                del assignment[var]
        return None

    def solve(self):
        """
        Start the backtracking search.
        """
        return self.backtrack({}, self.domains)


def main():
    # Define a simple scheduling problem.
    # Variables: Courses that need to be scheduled.
    variables = ['Course1', 'Course2', 'Course3', 'Course4']

    # Domains: Each course can be scheduled in one of these time slots.
    domains = {
        'Course1': ['9AM', '10AM', '11AM'],
        'Course2': ['9AM', '10AM', '11AM'],
        'Course3': ['9AM', '10AM', '11AM'],
        'Course4': ['9AM', '10AM', '11AM']
    }

    # Neighbors: Define which courses conflict (cannot be at the same time).
    # For instance, if Course1 and Course2 share a resource (like a profeesor or a room),
    # they cannot be scheduled simultaneously.
    neighbors = {
        'Course1': ['Course2', 'Course3'],  # Course1 conflicts with Course2 and Course3.
        'Course2': ['Course1', 'Course4'],
        'Course3': ['Course1'],
        'Course4': ['Course2']
    }

    # Create the CSP instance.
    scheduling_csp = CSP(variables, domains, neighbors)

    # Solve the CSP.
    solution = scheduling_csp.solve()
    if solution:
        print("Solution Found:")
        for course, time_slot in solution.items():
            print(f"  {course} -> {time_slot}")
    else:
        print("No solution exists.")

if __name__ == '__main__':
    main()
