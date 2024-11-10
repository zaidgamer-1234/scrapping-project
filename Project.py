import math
import sys
import pandas as pd
import time
import csv
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QWidget, QListWidget, QAbstractItemView, QMessageBox, QProgressBar, 
)
from Algorithms import*
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from web_scrapping import scrape_data

def load_products_from_csv(file_path):
    products = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                product = {
                    "Title": row["Title"],
                    "Location": row["Location"].replace("from ", "").strip(),
                    "Price": float(row["Price"].replace("$", "").replace(",", "")) if row["Price"] != "N/A" else 0.0,
                    "Discount": int(row["Discount"].replace("% off", "").strip()) if row["Discount"] != "N/A" else 0,
                    "Sec_Info": row["Sec_Info"],
                    "Shipping": float(row["Shipping"].replace("+$", "").replace(" shipping", "").strip()) if row["Shipping"] != "N/A" else 0.0,
                    "Sold": int(row["Sold"].replace(" sold", "").strip()) if row["Sold"] != "N/A" else 0
                }
                products.append(product)
            except ValueError:
                continue
    return pd.DataFrame(products)


class ScrapingThread(QThread):
    progress = pyqtSignal(int)  
    data_scraped = pyqtSignal(list)  

    def __init__(self, total_items=25000):
        super().__init__()
        self.total_items = total_items
        self._is_paused = False
        self._is_stopped = False
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        self.scraped_entries = 0

    def run(self):
        scraped_data = []

        for i in range(self.total_items):
            if self._is_stopped:
                break

            self.mutex.lock()
            if self._is_paused:
                self.wait_condition.wait(self.mutex)
            self.mutex.unlock()

            try:
                scraped_item = scrape_data()  
                self.df = load_products_from_csv('products.csv')

                if scraped_item:
                    scraped_data.append(scraped_item)
                    self.scraped_entries += 1

                progress_percentage = int((self.scraped_entries / self.total_items) * 100)
                self.progress.emit(progress_percentage)

                QApplication.processEvents()
            except Exception as e:
                print(f"Error during scraping: {e}")
                continue

            time.sleep(0.1)  

        self.data_scraped.emit(scraped_data)

    def pause(self):
        self.mutex.lock()
        self._is_paused = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self._is_paused = False
        self.wait_condition.wakeAll()
        self.mutex.unlock()

    def stop(self):
        self.mutex.lock()
        self._is_stopped = True
        self.mutex.unlock()


class SortingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.df = load_products_from_csv('products.csv')
        self.setWindowTitle("Sorting, Searching, and Scraping App")
        self.setGeometry(100, 100, 1000, 600)

        self.table_widget = QTableWidget()
        self.load_data()

        self.sort_btn = QPushButton("Sort")
        self.sort_btn.clicked.connect(self.sort_data)

        self.scraping_thread = ScrapingThread()

        self.scraping_thread.progress.connect(self.update_progress)
        self.scraping_thread.data_scraped.connect(self.on_data_scraped)

        self.algorithm_dropdown = QComboBox()
        self.algorithm_dropdown.addItems([
            "Bubble Sort", "Selection Sort", "Insertion Sort", "Merge Sort", "Quick Sort",
            "Counting Sort", "Radix Sort", "Bucket Sort", "OddEvenSort", "Gnome Sort"
        ])

        self.column_list_widget = QListWidget()
        self.column_list_widget.addItems(self.df.columns)
        self.column_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.column_list_widget.setFixedHeight(50)
        self.column_list_widget.setFixedWidth(200)

        self.column_list_widget.setStyleSheet("""QListWidget {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #76b900;  /* Green border */
            font-size: 12px;            /* Adjust font size as needed */
        }
        QListWidget::item {
            height: 15px;               /* Set item height */
        }
        QListWidget::item:selected {
            background-color: #76b900;  /* Selected item color */
            color: white;               /* Selected item text color */
        }
        """)

        self.search_input = QLineEdit()

        self.search_column_dropdown = QComboBox()
        self.search_column_dropdown.addItems(self.df.columns)
        self.search_column_dropdown.setFixedWidth(150)

        self.additional_search_column_dropdown = QComboBox()
        self.additional_search_column_dropdown.addItems(self.df.columns)
        self.additional_search_column_dropdown.setFixedWidth(150)

        self.search_condition_dropdown = QComboBox()
        self.search_condition_dropdown.addItems(["Contains", "Starts With", "Ends With"])
        self.search_condition_dropdown.setFixedWidth(150)

        self.operator_dropdown = QComboBox()
        self.operator_dropdown.addItems(["AND", "OR", "NOT"])
        self.operator_dropdown.setFixedWidth(100)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_data)

        self.reload_btn = QPushButton("Reload Data")
        self.reload_btn.clicked.connect(self.reload_data)

        self.scrap_btn = QPushButton("Start Scraping")
        self.scrap_btn.clicked.connect(self.start_scraping)

        self.pause_btn = QPushButton("Pause Scraping")
        self.pause_btn.clicked.connect(self.pause_scraping)

        self.resume_btn = QPushButton("Resume Scraping")
        self.resume_btn.clicked.connect(self.resume_scraping)

        self.stop_btn = QPushButton("Stop Scraping")
        self.stop_btn.clicked.connect(self.stop_scraping)

        self.progress_bar = QProgressBar()

        self.time_label = QLabel("Sorting time: 0 ms")

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Sort by:"))
        hbox.addWidget(self.column_list_widget)
        hbox.addWidget(self.algorithm_dropdown)
        hbox.addWidget(self.sort_btn)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("Search:"))
        hbox2.addWidget(self.search_input)
        hbox2.addWidget(self.search_column_dropdown)
        hbox2.addWidget(self.additional_search_column_dropdown)
        hbox2.addWidget(self.search_condition_dropdown)
        hbox2.addWidget(self.operator_dropdown)
        hbox2.addWidget(self.search_btn)
      

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.scrap_btn)
        hbox3.addWidget(self.pause_btn)
        hbox3.addWidget(self.resume_btn)
        hbox3.addWidget(self.stop_btn)
        hbox3.addWidget(self.progress_bar)

        layout.addLayout(hbox)
        layout.addLayout(hbox2)
        layout.addLayout(hbox3)
        layout.addWidget(self.time_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

         
        self.setStyleSheet("""
    QMainWindow {
        background-color: #1e1e1e;
    }
    QPushButton {
        background-color: #76b900;
        color: white;
        border-radius: 5px;
        padding: 5px;
        font-size: 12px;
        font-weight: bold;
        transition: background-color 0.3s ease;
        min-width: 50px;
        min-height: 25px;
    }
    QPushButton:hover {
        background-color: #8fdc00;
    }
    QPushButton:pressed {
        background-color: #4b8700;
    }
    QLineEdit {
        padding: 5px;
        border-radius: 5px;
        border: 1px solid #76b900;
        background-color: #2d2d2d;
        color: white;
        font-size: 12px;
        min-height: 25px;
    }
    QLineEdit:focus {
        border-color: #8fdc00;
    }
    QComboBox {
        padding: 5px;
        border-radius: 5px;
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #76b900;
        min-height: 25px;
    }
    QComboBox::drop-down {
        border-left: 1px solid #76b900;
    }
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #76b900;
    }
    QLabel {
        font-weight: bold;
        font-size: 14px;
        color: #76b900;
    }
    QTableWidget {
        background-color: #2d2d2d;
        color: white;
        gridline-color: #444444;
        font-size: 12px;
    }
    QHeaderView::section {
        background-color: #3d3d3d;
        color: #76b900;
        padding: 5px;
        border: 1px solid #444444;
    }
""")
    def start_scraping(self):
     total_items = 25000  
     self.scraping_thread = ScrapingThread(total_items)
     

     self.scraping_thread.progress.connect(self.update_progress_bar)
     self.scraping_thread.data_scraped.connect(self.handle_scraped_data)
     
     self.scraping_thread.start()


    def update_progress_bar(self, value):
      self.progress_bar.setValue(value)


    def handle_scraped_data(self, data):
        print("Scraping completed with data:", data)
    def pause_scraping(self):
     self.scraping_thread.pause()

    def resume_scraping(self):
     self.scraping_thread.resume()

    def stop_scraping(self):
     self.scraping_thread.stop()


    def load_data(self):
        self.table_widget.setColumnCount(len(self.df.columns))
        self.table_widget.setRowCount(len(self.df))
        self.table_widget.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))

    def reload_data(self):
        self.df = load_products_from_csv('products.csv')
        self.load_data()

    def start_scraping(self):
        self.scraping_thread.start()

    def pause_scraping(self):
        self.scraping_thread.pause()

    def resume_scraping(self):
        self.scraping_thread.resume()

    def stop_scraping(self):
        self.scraping_thread.stop()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_data_scraped(self, scraped_data):
        # Handle the scraped data
        new_df = pd.DataFrame(scraped_data)
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self.load_data()
    
    def load_data(self):
        self.table_widget.setColumnCount(len(self.df.columns))
        self.table_widget.setRowCount(len(self.df))
        self.table_widget.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))

    
    def reload_data(self):
        self.df = load_products_from_csv('products.csv')  
        self.load_data()  

                

    def sort_data(self):
     selected_columns = self.column_list_widget.selectedItems()
     if not selected_columns:
         QMessageBox.warning(self, "Selection Error", "Please select at least one column to sort by.")
         return
 
     self.sort_btn.setText("Sorting...")
     self.sort_btn.setEnabled(False)
     QApplication.processEvents()
 
     start_time = time.time()
 
     data_records = self.df.to_dict('records')
     selected_algorithm = self.algorithm_dropdown.currentText()
 
     column_keys = [item.text() for item in selected_columns]
 
     try:
         if selected_algorithm == "Bubble Sort":
             data_records = BubbleSort(data_records, column_keys)
         elif selected_algorithm == "Selection Sort":
           
                 data_records = SelectionSort(data_records, column_keys)
         elif selected_algorithm == "Insertion Sort":
           
                 data_records = InsertionSort(data_records, column_keys)
         elif selected_algorithm == "Merge Sort":
                 data_records = MergeSort(data_records, column_keys)
         elif selected_algorithm == "Quick Sort":
                 data_records = QuickSort(data_records, column_keys)
         elif selected_algorithm == "Counting Sort":
                 data_records = CountingSort(data_records, column_keys)
         elif selected_algorithm == "Radix Sort":
                 data_records = RadixSort(data_records, column_keys)
         elif selected_algorithm == "Bucket Sort":
                 data_records = BubbleSort(data_records, column_keys)
         elif selected_algorithm == "OddEvenSort":
                 data_records = odd_even_sort(data_records, column_keys)
         elif selected_algorithm == "Gnome Sort":
                 data_records = gnome_sort(data_records, column_keys)
         else:
             raise ValueError("Invalid sorting algorithm selected.")
 
         self.df = pd.DataFrame(data_records)
 
     except Exception as e:
         QMessageBox.critical(self, "Sorting Error", str(e))
         self.sort_btn.setText("Sort")
         self.sort_btn.setEnabled(True)
         return
 
     end_time = time.time()
     self.load_data()
     elapsed_time_ms = (end_time - start_time) * 1000
     self.time_label.setText(f"Sorting time: {elapsed_time_ms:.2f} ms")
 
     self.sort_btn.setText("Sort")
     self.sort_btn.setEnabled(True)

    def search_data(self):

        search_text = self.search_input.text().strip()
        search_column = self.search_column_dropdown.currentText()
        additional_column = self.additional_search_column_dropdown.currentText()
        search_condition = self.search_condition_dropdown.currentText()
        operator = self.operator_dropdown.currentText()

        # Get the boolean mask based on the selected condition
        if search_condition == "Contains":
            mask1 = self.df[search_column].astype(str).str.contains(search_text, na=False)
            mask2 = self.df[additional_column].astype(str).str.contains(search_text, na=False)
        elif search_condition == "Starts With":
            mask1 = self.df[search_column].astype(str).str.startswith(search_text, na=False)
            mask2 = self.df[additional_column].astype(str).str.startswith(search_text, na=False)
        elif search_condition == "Ends With":
            mask1 = self.df[search_column].astype(str).str.endswith(search_text, na=False)
            mask2 = self.df[additional_column].astype(str).str.endswith(search_text, na=False)

        if operator == "AND":
            final_mask = mask1 & mask2
        elif operator == "OR":
            final_mask = mask1 | mask2
        elif operator == "NOT":
            final_mask = ~mask1


        filtered_df = self.df[final_mask]

        if filtered_df.empty:
            self.table_widget.setRowCount(0)
        else:
            self.table_widget.setRowCount(len(filtered_df))
            for i in range(len(filtered_df)):
                for j in range(len(filtered_df.columns)):
                    self.table_widget.setItem(i, j, QTableWidgetItem(str(filtered_df.iloc[i, j])))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SortingApp()
    window.show()
    sys.exit(app.exec_())
