import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from gurobipy import Model, GRB, GurobiError
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AdvertisingGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advertising Budget Allocator")
        self.setGeometry(100, 100, 900, 700)

        # Apply modern stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7fa; }
            QLabel { font-family: 'Segoe UI', sans-serif; color: #2c3e50; }
            QLineEdit { 
                padding: 10px; 
                border: 1px solid #d1d9e6; 
                border-radius: 8px; 
                background-color: #ffffff; 
                font-size: 16px; 
            }
            QCheckBox { 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 14px; 
                color: #2c3e50; 
                padding: 5px; 
            }
            QPushButton { 
                background-color: #2c3e50; 
                color: white; 
                padding: 16px 32px; 
                border: none; 
                border-radius: 8px; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 18px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #1f2a44; }
            QPushButton:pressed { background-color: #17202a; }
        """)

        # Central widget and main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Title
        title_label = QtWidgets.QLabel("Advertising Budget Allocator")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Input panel
        input_widget = QtWidgets.QWidget()
        input_widget.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 15px;")
        input_layout = QtWidgets.QVBoxLayout(input_widget)
        input_layout.setSpacing(20)
        input_layout.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(input_widget)

        # Budget input
        budget_container = QtWidgets.QWidget()
        budget_container_layout = QtWidgets.QHBoxLayout(budget_container)
        budget_container_layout.setAlignment(QtCore.Qt.AlignCenter)
        budget_container_layout.setContentsMargins(0, 0, 0, 0)
        budget_container_layout.setSpacing(10)
        budget_label = QtWidgets.QLabel("Budget:")
        budget_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        budget_container_layout.addWidget(budget_label)
        self.budget_input = QtWidgets.QLineEdit()
        self.budget_input.setText("10000")
        self.budget_input.setFixedWidth(200)
        self.budget_input.setPlaceholderText("$ Enter budget")
        validator = QtGui.QDoubleValidator(0.0, 1000000.0, 2)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.budget_input.setValidator(validator)
        budget_container_layout.addWidget(self.budget_input)
        input_layout.addWidget(budget_container, alignment=QtCore.Qt.AlignCenter)

        # Desired reach input
        reach_container = QtWidgets.QWidget()
        reach_container_layout = QtWidgets.QHBoxLayout(reach_container)
        reach_container_layout.setAlignment(QtCore.Qt.AlignCenter)
        reach_container_layout.setContentsMargins(0, 0, 0, 0)
        reach_container_layout.setSpacing(10)
        reach_label = QtWidgets.QLabel("Desired Reach:")
        reach_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        reach_container_layout.addWidget(reach_label)
        self.reach_input = QtWidgets.QLineEdit()
        self.reach_input.setText("50000")
        self.reach_input.setFixedWidth(200)
        self.reach_input.setPlaceholderText("Enter desired reach")
        reach_validator = QtGui.QDoubleValidator(0.0, 10000000.0, 2)
        reach_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.reach_input.setValidator(reach_validator)
        reach_container_layout.addWidget(self.reach_input)
        input_layout.addWidget(reach_container, alignment=QtCore.Qt.AlignCenter)

        # Checkboxes for channels
        checkbox_layout = QtWidgets.QHBoxLayout()
        checkbox_layout.setSpacing(15)
        self.channel_checkboxes = []
        for channel in ["Facebook", "Instagram", "TikTok", "Online Ads"]:
            checkbox = QtWidgets.QCheckBox(channel)
            checkbox.setChecked(True)  # Checked by default
            self.channel_checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox)
        input_layout.addLayout(checkbox_layout)

        solve_button = QtWidgets.QPushButton("Solve")
        solve_button.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
        solve_button.clicked.connect(self.solve_problem)
        solve_button.setFixedWidth(160)
        solve_button.setMinimumHeight(50)
        solve_button.setStyleSheet("background-color: #2c3e50;")
        input_layout.addWidget(solve_button, alignment=QtCore.Qt.AlignCenter)

        # Results panel
        self.result_widget = QtWidgets.QWidget()
        self.result_widget.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 15px;")
        result_layout = QtWidgets.QVBoxLayout(self.result_widget)
        result_layout.setSpacing(15)
        main_layout.addWidget(self.result_widget)

        # Result text
        self.result_label = QtWidgets.QLabel("Enter budget and reach, select at least two channels, and click 'Solve' to see results.")
        self.result_label.setStyleSheet("font-size: 14px; color: #2c3e50; background-color: #f5f7fa; padding: 10px; border-radius: 5px;")
        self.result_label.setWordWrap(True)
        result_layout.addWidget(self.result_label)

        # Matplotlib canvas for bar chart
        try:
            plt.style.use('seaborn-v0_8')
        except:
            plt.style.use('default')
        self.figure, self.ax = plt.subplots(figsize=(6, 5.5))  # Increased height
        self.canvas = FigureCanvas(self.figure)
        result_layout.addWidget(self.canvas)

        main_layout.addStretch()

        # channel data
        self.channels = ["Facebook", "Instagram", "TikTok", "Online Ads"]
        self.costs = [1000, 800, 500, 300]
        self.reaches = [20000, 15000, 10000, 5000]
        self.conv_rates = [0.02, 0.03, 0.04, 0.01]
        self.min_ads = [1, 0, 2, 0]  # Renamed for clarity
        self.max_ads = [5, 6, 8, 20]  # Renamed for clarity

    def solve_problem(self):
        """Solve the optimization problem using Gurobi."""
        try:
            # Retrieve and validate budget
            budget_text = self.budget_input.text()
            if not budget_text:
                QtWidgets.QMessageBox.critical(self, "Input Error", "Please enter a valid budget.")
                return
            budget = float(budget_text)

            # retrieve and validate desired reach
            reach_text = self.reach_input.text()
            if not reach_text:
                QtWidgets.QMessageBox.critical(self, "Input Error", "Please enter a valid desired reach.")
                return
            desired_reach = float(reach_text)

            #get selected channels
            selected_indices = [i for i, checkbox in enumerate(self.channel_checkboxes) if checkbox.isChecked()]
            if len(selected_indices) < 2:
                QtWidgets.QMessageBox.critical(self, "Input Error", "Please select at least two channels.")
                return

            # Gurobi model
            model = Model("Advertising_Allocation")
            model.setParam('OutputFlag', 0)
            x = [model.addVar(lb=self.min_ads[i], ub=self.max_ads[i], vtype=GRB.CONTINUOUS, name=f"Channel_{i}")
                 for i in selected_indices]

            # objective: maximize conversions for selected channels
            model.setObjective(sum(self.reaches[i] * self.conv_rates[i] * x[j] for j, i in enumerate(selected_indices)), GRB.MAXIMIZE)

            # constraint: budget for selected channels
            model.addConstr(sum(self.costs[i] * x[j] for j, i in enumerate(selected_indices)) <= budget, "Budget")

            # Constraint: desired reach for selected channels
            model.addConstr(sum(self.reaches[i] * x[j] for j, i in enumerate(selected_indices)) >= desired_reach, "Reach")

            # Optimize
            model.optimize()

            # Display results
            if model.status == GRB.OPTIMAL:
                allocations = [0] * 4 
                for j, i in enumerate(selected_indices):
                    allocations[i] = x[j].x
                total_conversions = model.objVal
                total_cost = sum(self.costs[i] * allocations[i] for i in range(4))
                total_reach = sum(self.reaches[i] * allocations[i] for i in range(4))
                result = (f"<b>Optimal Conversions:</b> {total_conversions:.2f}<br>"
                          f"<b>Total Cost:</b> ${total_cost:.2f}<br>"
                          f"<b>Total Reach:</b> {total_reach:.2f}<br>"
                          f"<b>Allocation:</b><br>")
                for i, channel in enumerate(self.channels):
                    result += f"  {channel}: ${self.costs[i] * allocations[i]:.2f}<br>"  # Show budget allocated
                self.result_label.setText(result)

                # Plot bar chart for selected channels
                self.ax.clear()
                selected_channels = [self.channels[i] for i in selected_indices]
                selected_budgets = [self.costs[i] * allocations[i] for i in selected_indices]  # Budget instead of ads
                sns.barplot(x=selected_budgets, y=selected_channels, ax=self.ax, color='#2c3e50')
                self.ax.set_title("Advertising Allocation", fontsize=14, pad=10)
                self.ax.grid(True, axis='x', linestyle='--', alpha=0.7)
                self.ax.set_xlim(0, max(selected_budgets) * 1.2 if selected_budgets else 1)
                self.ax.tick_params(axis='y', labelsize=12) 
                self.figure.tight_layout()
                self.canvas.draw()
            else:
                self.result_label.setText("No optimal solution found. Check budget, reach, or channel selection.")
                self.ax.clear()
                self.canvas.draw()

        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Input Error", "Please enter valid numeric values for budget and reach.")
        except GurobiError as e:
            QtWidgets.QMessageBox.critical(self, "Gurobi Error", f"Gurobi error: {e.message}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdvertisingGUI()
    window.show()
    sys.exit(app.exec_())