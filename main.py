import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from staff_scheduling import StaffSchedulingApp
from advertising_budget_allocator import AdvertisingGUI

class ProblemSelectorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimization Problem Selector")
        self.setGeometry(300, 300, 600, 400)
        
        # Apply modern stylesheet
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #f0f2f5; 
            }
            QLabel { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                color: #2c3e50; 
                font-size: 18px;
            }
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 16px; 
                font-weight: bold; 
                min-width: 250px;
            }
            QPushButton:hover { 
                background-color: #2980b9; 
            }
            QPushButton:pressed { 
                background-color: #1f6aa5; 
            }
        """)
        
        # Central widget and main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Title
        title_label = QtWidgets.QLabel("Select Optimization Problem")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QtWidgets.QLabel("Choose an optimization problem to solve:")
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # Advertising button
        ad_button = QtWidgets.QPushButton("Advertising Budget Allocator")
        ad_button.setIcon(QtGui.QIcon.fromTheme("contact-new"))
        ad_button.clicked.connect(lambda: self.run_app("advertising"))
        main_layout.addWidget(ad_button, alignment=QtCore.Qt.AlignCenter)
        
        # Staff scheduling button
        staff_button = QtWidgets.QPushButton("Staff Scheduling Optimization")
        staff_button.setIcon(QtGui.QIcon.fromTheme("appointment-new"))
        staff_button.clicked.connect(lambda: self.run_app("staff"))
        main_layout.addWidget(staff_button, alignment=QtCore.Qt.AlignCenter)
        
        # Exit button
        exit_button = QtWidgets.QPushButton("Exit")
        exit_button.setIcon(QtGui.QIcon.fromTheme("application-exit"))
        exit_button.clicked.connect(self.close)
        exit_button.setStyleSheet("background-color: #e74c3c;")
        main_layout.addWidget(exit_button, alignment=QtCore.Qt.AlignCenter)
    
    def run_app(self, app_type):
        try:
            if app_type == "advertising":
                # First check if the module is already imported
                self.advertising_window = AdvertisingGUI()
                self.advertising_window.show()
            
            elif app_type == "staff":
                # First check if the module is already imported
                self.staff_window = StaffSchedulingApp()
                self.staff_window.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ProblemSelectorApp()
    window.show()
    sys.exit(app.exec_())