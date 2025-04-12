# Scheduling-CSP-Solver

---

The project is organized in the following files:
- csp.py: Contains the core CSP class and search methods.
- constraints.py: Contains functions for all hard constraints.
- preferences.py: Contains functions for soft constraint scoring.
- main.py: Builds the scheduling problem instance and runs the solver.

---

The basic setting of the problem: 

- There are two academic terms and each term has courses that run either MWF (Monday/Wednesday/Friday) or TTH (Tuesday/Thursday).
- Only 5 courses (e.g. 3 MWF, 2 TTH) are available per each term.
- The student has already completed MATH 134 before to prove prerequisite_constraint_transitive (e.g. CMPUT 204 requires MATH 134 or MATH 144, CMPUT 366 requires CMPUT 204).
- The same room can be used for only 2 courses. 
