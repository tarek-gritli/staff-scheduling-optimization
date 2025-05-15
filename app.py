import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QPushButton, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from gurobipy import Model, GRB, quicksum


class StaffSchedulingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Staff Scheduling Optimization")
        self.setGeometry(200, 200, 1000, 850)

        layout = QVBoxLayout()

        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #34495e;
            }
            QLineEdit {
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                background-color: #ffffff;
                color: #34495e;
            }
            QTableWidget {
                border: 1px solid #34495e;
                font-size: 14px;
                background-color: #ffffff;
                color: #34495e;
            }
            QPushButton {
                background-color: #3498db;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                padding: 10px;
}
            QPushButton:hover {
                background-color: #2980b9;
            }

        """)

        self.container = QWidget()
        self.container.setLayout(layout)
        self.setCentralWidget(self.container)

        # Title
        title = QLabel("Staff Scheduling Optimization")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Input Grid
        self.input_grid = QGridLayout()
        layout.addLayout(self.input_grid)

        self.add_input_field(
            "Number of Employees (E):",
            "Total number of employees available for scheduling.",
            0,
            "employees_input",
        )
        self.add_input_field(
            "Number of Shifts per Day (S):",
            "Number of shifts required per day (e.g., Morning, Evening, Night).",
            1,
            "shifts_input",
        )
        self.add_input_field(
            "Number of Days (T):",
            "Total number of days to schedule (e.g., 7 for one week).",
            2,
            "days_input",
        )
        self.add_table(
            "Cost per shift (matrix for all employees and days):",
            "Enter the cost for each employee working each shift on each day.",
            3,
            "costs_table",
        )
        self.add_table(
            "Availability (1 for available, 0 for not):",
            "Enter 1 if the employee is available for the shift, 0 otherwise.",
            4,
            "availability_table",
        )
        self.add_table(
            "Required employees per shift per day:",
            "Enter the number of employees required for each shift on each day.",
            5,
            "requirements_table",
        )
        self.add_input_field(
            "Max Shifts per Employee (M):",
            "Maximum number of shifts an employee can work during the scheduling period.",
            6,
            "max_shifts_input",
        )

        # Run Button
        self.run_button = QPushButton("Solve")
        self.run_button.setCursor(Qt.PointingHandCursor)
        self.run_button.clicked.connect(self.run_optimization)
        layout.addWidget(self.run_button)

        # Results
        self.output_label = QLabel("Results:")
        layout.addWidget(self.output_label)

        self.output_area = QTableWidget()
        self.output_area.setRowCount(0)
        self.output_area.setColumnCount(3)
        self.output_area.setHorizontalHeaderLabels(["Employee", "Day", "Shift"])
        layout.addWidget(self.output_area)

    def add_input_field(self, label_text, tooltip, row, attribute_name):
        """Add a single-line input field with a tooltip."""
        label = QLabel(label_text)
        label.setToolTip(tooltip)
        self.input_grid.addWidget(label, row, 0)
        field = QLineEdit()
        field.setToolTip(tooltip)
        field.textChanged.connect(self.update_matrices)  # Trigger dynamic matrix resizing
        setattr(self, attribute_name, field)
        self.input_grid.addWidget(field, row, 1)

    def add_table(self, label_text, tooltip, row, attribute_name):
        """Add a table input for matrix data with a tooltip."""
        label = QLabel(label_text)
        label.setToolTip(tooltip)
        self.input_grid.addWidget(label, row, 0)
        table = QTableWidget(0, 0)
        table.setToolTip(tooltip)
        setattr(self, attribute_name, table)
        self.input_grid.addWidget(table, row, 1)

    def update_matrices(self):
        """Resize matrices dynamically based on employee, shift, and day input."""
        try:
            num_employees = int(self.employees_input.text()) if self.employees_input.text().isdigit() else 0
            num_shifts = int(self.shifts_input.text()) if self.shifts_input.text().isdigit() else 0
            num_days = int(self.days_input.text()) if self.days_input.text().isdigit() else 0

            # Update Costs Table (Employees x Days) x Shifts
            self.resize_table(
                self.costs_table, num_employees * num_days, num_shifts, "Employee {e} - Day {d}", "Shift {s}"
            )

            # Update Availability Table (Employees x Days) x Shifts
            self.resize_table(
                self.availability_table, num_employees * num_days, num_shifts, "Employee {e} - Day {d}", "Shift {s}"
            )

            # Update Requirements Table Days x Shifts
            self.resize_table(
                self.requirements_table, num_days, num_shifts, "Day {d}", "Shift {s}"
            )
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid input values for employees, shifts, or days.")

    def resize_table(self, table, rows, cols, row_label_format, col_label_format):
        """Resize a QTableWidget to the specified rows and columns, with headers."""
        table.setRowCount(rows)
        table.setColumnCount(cols)

        # Set row headers
        for row in range(rows):
            if "{e}" in row_label_format and "{d}" in row_label_format:
                employee = (row // (rows // cols)) + 1
                day = (row % (rows // cols)) + 1
                table.setVerticalHeaderItem(row, QTableWidgetItem(row_label_format.format(e=employee, d=day)))
            elif "{d}" in row_label_format:
                table.setVerticalHeaderItem(row, QTableWidgetItem(row_label_format.format(d=row + 1)))

        # Set column headers
        for col in range(cols):
            table.setHorizontalHeaderItem(col, QTableWidgetItem(col_label_format.format(s=col + 1)))

    def parse_table(self, table, expected_rows, expected_cols, table_name):
        rows = table.rowCount()
        cols = table.columnCount()

        # Check if the table has the expected dimensions
        if rows != expected_rows or cols != expected_cols:
            raise ValueError(
                f"The {table_name} table must have exactly {expected_rows} rows and {expected_cols} columns. "
                f"Found {rows} rows and {cols} columns."
            )

        # Parse the data into a 2D list
        data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = table.item(row, col)

                # Check if the cell is empty
                if item is None or item.text().strip() == "":
                    raise ValueError(
                        f"The {table_name} table has an empty cell at row {row + 1}, column {col + 1}."
                    )

                # Try to convert the cell data to a float
                try:
                    value = float(item.text().strip())
                    row_data.append(value)
                except ValueError:
                    raise ValueError(
                        f"The {table_name} table contains invalid data at row {row + 1}, column {col + 1}: "
                        f"'{item.text().strip()}' is not a valid number."
                    )
            data.append(row_data)

        return data

    def run_optimization(self):
        try:
            # Validate numeric inputs
            try:
                num_employees = int(self.employees_input.text())
                num_shifts = int(self.shifts_input.text())
                num_days = int(self.days_input.text())
                max_shifts = int(self.max_shifts_input.text())
                
                # Check if all inputs are positive integers
                
                

                if num_employees <= 0 or num_shifts <= 0 or num_days <= 0 or max_shifts <= 0:
                    raise ValueError("All numeric inputs must be positive integers.")

            except ValueError as e:
                QMessageBox.warning(self, "Input Error", "Invalid input for employees, shifts, days, or max shifts.")
                return

            # Parse tables
            try:
                costs = self.parse_table(self.costs_table, num_employees * num_days, num_shifts, "Costs")
                availability = self.parse_table(self.availability_table, num_employees * num_days, num_shifts, "Availability")
                requirements = self.parse_table(self.requirements_table, num_days, num_shifts, "Requirements")
            except ValueError as e:
                QMessageBox.critical(self, "Table Error", str(e))
                return

            # Initialize Gurobi model
            model = Model("StaffScheduling")

            # Define decision variables: x[e, d, s] = 1 if employee e is assigned to shift s on day d
            x = model.addVars(num_employees, num_days, num_shifts, vtype=GRB.BINARY, name="x")

            # Objective: Minimize costs
            model.setObjective(
                quicksum(
                    costs[e * num_days + d][s] * x[e, d, s]
                    for e in range(num_employees)
                    for d in range(num_days)
                    for s in range(num_shifts)
                ),
                GRB.MINIMIZE,
            )

            # Constraints
            # Employee availability
            for e in range(num_employees):
                for d in range(num_days):
                    for s in range(num_shifts):
                        if availability[e * num_days + d][s] == 0:
                            model.addConstr(x[e, d, s] == 0, f"Availability_{e}_{d}_{s}")

            # Shift requirements
            for d in range(num_days):
                for s in range(num_shifts):
                    model.addConstr(
                        quicksum(x[e, d, s] for e in range(num_employees)) == requirements[d][s],
                        f"Requirements_{d}_{s}",
                    )

            # Max shifts per employee
            for e in range(num_employees):
                model.addConstr(
                    quicksum(x[e, d, s] for d in range(num_days) for s in range(num_shifts)) <= max_shifts,
                    f"MaxShifts_{e}",
                )

            # Solve the optimization problem
            model.optimize()

            # Display results
            self.output_area.setRowCount(0)  # Clear existing results
            if model.status == GRB.OPTIMAL:
                for e in range(num_employees):
                    for d in range(num_days):
                        for s in range(num_shifts):
                            if x[e, d, s].x > 0.5:  # If employee e is assigned to shift s on day d
                                row_pos = self.output_area.rowCount()
                                self.output_area.insertRow(row_pos)
                                self.output_area.setItem(row_pos, 0, QTableWidgetItem(f"Employee {e+1}"))
                                self.output_area.setItem(row_pos, 1, QTableWidgetItem(f"Day {d+1}"))
                                self.output_area.setItem(row_pos, 2, QTableWidgetItem(f"Shift {s+1}"))
            elif model.status == GRB.INFEASIBLE:
                QMessageBox.warning(self, "No Solution", "No feasible solution found.")
            elif model.status == GRB.UNBOUNDED:
                QMessageBox.warning(self, "No Solution", "The model is unbounded. Check your constraints.")
            else:
                QMessageBox.warning(self, "No Solution", f"Optimization failed. Gurobi status code: {model.status}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StaffSchedulingApp()
    window.show()
    sys.exit(app.exec_())
