import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt6.QtGui import QAction
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QIcon, QPixmap
import psycopg2

qtCreatorFile = "Milestone3.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Milestone3(QMainWindow):
    def __init__(self):
        super(Milestone3, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadStateList()
        self.ui.stateList.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.ui.zipcode.itemSelectionChanged.connect(self.zipcodeChanged)
        # self.ui.categories.itemSelectionChanged.connect(self.categoriesChanged)
        self.ui.searchButton.clicked.connect(self.on_searchButton_clicked)
        self.ui.Clear.clicked.connect(self.clear_business_table)
        self.ui.zipcode.itemSelectionChanged.connect(self.zipcodeChanged)
        self.ui.Refresh.clicked.connect(self.on_refreshButton_clicked)

     
        



    def executeQuery(self, sql_str):
        try:
            conn = psycopg2.connect("dbname='Yelp' user='postgres' host='localhost' password='Haloplayer7@'")
        except:
            print("Unable to connect to database!")
        cur = conn.cursor()
        cur.execute(sql_str)
        conn.commit()
        result = cur.fetchall()
        conn.close()
        return result

    def loadStateList(self):
        self.ui.stateList.clear()
        sql_str = "SELECT distinct state FROM business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.stateList.addItem(row[0])
        except:
            print("Loading States Failed!")
        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()

    def stateChanged(self):
        self.ui.cityList.clear()
        state = self.ui.stateList.currentText()

        if (self.ui.stateList.currentIndex() >= 0):
            sql_str = "SELECT distinct city FROM business WHERE state ='" + state + "' ORDER BY city;"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.cityList.addItem(row[0])
            except:
                print("Loading Cities Failed!")

                

    def cityChanged(self):
        self.ui.zipcode.clear()
        state = self.ui.stateList.currentText()
        try:
            city = self.ui.cityList.selectedItems()[0].text()
        except:
            city =''
        sql_str = "SELECT distinct zipcode FROM business WHERE state = '" + state + "' AND city = '" + city + "' ORDER BY zipcode;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.zipcode.addItem(row[0])
        except:
            print("Loading Zip Codes Failed!")


    def zipcodeChanged(self):
        self.ui.categories.clear()
        state = self.ui.stateList.currentText()
        try:
            city = self.ui.cityList.selectedItems()[0].text()
        except:
            city =''
        try:
            zip_code = self.ui.zipcode.selectedItems()[0].text()
        except:
            zip_code =''
        
        if zip_code:
            self.update_number_of_businesses(zip_code)
            population = self.get_population_by_zipcode(zip_code)
            if population is not None:
                self.ui.total_pop.setPlainText(f"{population}") # Update the QTextEdit with the population
            else:
                self.ui.total_pop.setPlainText("N/A")
        mean_income = self.get_average_income_by_zipcode(zip_code)
        if mean_income is not None:
            self.ui.average_income.setPlainText(f"{mean_income}") # Update the QTextEdit with the average income
        else:
            self.ui.average_income.setPlainText("N/A")

        try:
            sql_str = "SELECT distinct category_name FROM categories WHERE business_id IN (SELECT business_id FROM business WHERE state = '" + state + "' AND city = '" + city + "' AND zipcode = '" + zip_code + "') ORDER BY category_name;"
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.categories.addItem(row[0])

            # Get the number of businesses per category and display them in the top_categories table widget
            sql_str = "SELECT category_name, COUNT(*) as count FROM categories WHERE business_id IN (SELECT business_id FROM business WHERE state = '" + state + "' AND city = '" + city + "' AND zipcode = '" + zip_code + "') GROUP BY category_name ORDER BY count DESC;"
            category_counts = self.executeQuery(sql_str)
            self.display_top_categories(category_counts)
        
        except:
            print("Loading Categories Failed!")
    
    # def categoriesChanged(self):
    #     if (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0) and (len(self.ui.zipcode.selectedItems()) > 0) and (len(self.ui.categories.selectedItems()) > 0):
    #         state = self.ui.stateList.currentText()
    #         city = self.ui.cityList.selectedItems()[0].text()
    #         zip_code = self.ui.zipcode.selectedItems()[0].text()
    #         category = self.ui.categories.selectedItems()[0].text()
    #         try:
    #             zip_code = self.ui.zipcode.selectedItems()[0].text()
    #         except:
    #             zip_code =''
    #         try:
    #             category = self.ui.categories.selectedItems()[0].text()
    #         except:
    #             category =''
    #         sql_str = "SELECT name, city, state, zipcode, category_name FROM (SELECT * from business NATURAL JOIN categories) as nj WHERE state = '" + state + "' AND city = '" + city + "' AND zipcode = '" + zip_code + "' AND category_name = '" + category + "' ORDER BY name;"
    #         try:
    #             results = self.executeQuery(sql_str)
    #             self.ui.businessTable.setColumnCount(len(results[0]))
    #             self.ui.businessTable.setRowCount(len(results))
    #             self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'City', 'State', 'Zip Code', 'Categories'])
    #             self.ui.businessTable.resizeColumnsToContents()
    #             self.ui.businessTable.setColumnWidth(0, 300)
    #             self.ui.businessTable.setColumnWidth(1, 100)
    #             self.ui.businessTable.setColumnWidth(2, 50)
    #             self.ui.businessTable.setColumnWidth(3, 75)
    #             self.ui.businessTable.setColumnWidth(4, 300)
    #             currentRowCount = 0
    #             for row in results:
    #                 for colCount in range (0, len(results[0])):
    #                     self.ui.businessTable.setItem(currentRowCount, colCount, QTableWidgetItem(row[colCount]))
    #                 currentRowCount += 1

    #         except:
    #             print("Loading Names Failed!")
        

    def on_searchButton_clicked(self):
        # Handle the button click event here
        print("Search button clicked")
        if (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0) and (len(self.ui.zipcode.selectedItems()) > 0) and (len(self.ui.categories.selectedItems()) > 0):
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()
            zip_code = self.ui.zipcode.selectedItems()[0].text()
            category = self.ui.categories.selectedItems()[0].text()
            try:
                zip_code = self.ui.zipcode.selectedItems()[0].text()
            except:
                zip_code =''
            try:
                category = self.ui.categories.selectedItems()[0].text()
            except:
                category =''
            sql_str = "SELECT name, address, city, state, zipcode, category_name, numcheckins, stars, review_count, reviewrating  FROM (SELECT * from business NATURAL JOIN categories) as nj WHERE state = '" + state + "' AND city = '" + city + "' AND zipcode = '" + zip_code + "' AND category_name = '" + category + "'  ORDER BY name;"
            try:
                results = self.executeQuery(sql_str)
                self.ui.businessTable.setColumnCount(len(results[0]))
                self.ui.businessTable.setRowCount(len(results))
                self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'address', 'City', 'State', 'Zip Code', 'Categories', 'numcheckins', 'stars', 'review_count', 'reviewrating'])
                self.ui.businessTable.resizeColumnsToContents()
                self.ui.businessTable.setColumnWidth(0, 300)
                self.ui.businessTable.setColumnWidth(1, 100)
                self.ui.businessTable.setColumnWidth(2, 50)
                self.ui.businessTable.setColumnWidth(3, 75)
                self.ui.businessTable.setColumnWidth(4, 300)
                self.ui.businessTable.setColumnWidth(5, 300)
                self.ui.businessTable.setColumnWidth(6, 300)
                self.ui.businessTable.setColumnWidth(7, 300)
                self.ui.businessTable.setColumnWidth(8, 300)    
                self.ui.businessTable.setColumnWidth(9, 300)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.businessTable.setItem(
                            currentRowCount, colCount, QTableWidgetItem(str(row[colCount]))
                        )
                    currentRowCount += 1

            except:
                print("Loading Names Failed!")


    def clear_business_table(self):
        self.ui.businessTable.setRowCount(0)
        self.ui.businessTable.setColumnCount(0)
        self.ui.businessTable.setHorizontalHeaderLabels([])



    def update_number_of_businesses(self, zip_code):
        sql_str = f"SELECT COUNT(*) FROM business WHERE zipcode = '{zip_code}';"
        try:
            result = self.executeQuery(sql_str)
            count = result[0][0]
            self.ui.number_business.setPlainText(f"{count}") # Update the QTextEdit
        except Exception as e:
            print(f"Error{e}")

    def get_population_by_zipcode(self, zip_code):
        sql_str = f"SELECT population FROM zipcodedata WHERE zipcode = '{zip_code}';"
        try:
            result = self.executeQuery(sql_str)
            population = result[0][0]
            return population
        except Exception as e:
            print(f"Error getting population: {e}")
            return None
        
    def get_average_income_by_zipcode(self, zip_code):
        sql_str = f"SELECT meanincome FROM zipcodedata WHERE zipcode = '{zip_code}';"
        try:
            result = self.executeQuery(sql_str)
            mean_income = result[0][0]
            return mean_income
        except Exception as e:
            print(f"Error getting average income: {e}")
            return None


    def display_top_categories(self, category_counts):
        self.ui.top_categories.setRowCount(len(category_counts))
        self.ui.top_categories.setColumnCount(2)
        self.ui.top_categories.setHorizontalHeaderLabels(["Category", "Number of Businesses"])

        for i, (category, count) in enumerate(category_counts):
            self.ui.top_categories.setItem(i, 0, QTableWidgetItem(category))
            self.ui.top_categories.setItem(i, 1, QTableWidgetItem(str(count)))

        self.ui.top_categories.resizeColumnsToContents()
    
    def display_popular_businesses(self, popular_businesses):
        self.ui.popular_bus.setRowCount(len(popular_businesses))
        self.ui.popular_bus.setColumnCount(4)
        self.ui.popular_bus.setHorizontalHeaderLabels(["Business Name", "Stars", "Review Rating", "Number of Reviews"])

        for i, (name, stars, review_rating, review_count) in enumerate(popular_businesses):
            self.ui.popular_bus.setItem(i, 0, QTableWidgetItem(name))
            self.ui.popular_bus.setItem(i, 1, QTableWidgetItem(str(stars)))
            self.ui.popular_bus.setItem(i, 2, QTableWidgetItem(str(review_rating)))
            self.ui.popular_bus.setItem(i, 3, QTableWidgetItem(str(review_count)))

        self.ui.popular_bus.resizeColumnsToContents()


    def display_successful_businesses(self, successful_businesses):
        self.ui.Successful_bus.setRowCount(len(successful_businesses))
        self.ui.Successful_bus.setColumnCount(3)
        self.ui.Successful_bus.setHorizontalHeaderLabels(["Business Name", "Number of Reviews", "Number of Check-ins"])

        for i, (name, review_count, numcheckins) in enumerate(successful_businesses):
            self.ui.Successful_bus.setItem(i, 0, QTableWidgetItem(name))
            self.ui.Successful_bus.setItem(i, 1, QTableWidgetItem(str(review_count)))
            self.ui.Successful_bus.setItem(i, 2, QTableWidgetItem(str(numcheckins)))

        self.ui.Successful_bus.resizeColumnsToContents()



    def get_popular_businesses_by_zipcode(self, zip_code):
        sql_str = f"""
        SELECT name, stars, reviewrating, review_count FROM business WHERE zipcode = '{zip_code}' AND stars >= 4 AND reviewrating >= 4 AND review_count >= 5 ORDER BY stars DESC, reviewrating DESC, review_count DESC; """
        try:
            result = self.executeQuery(sql_str)
            return result
        except Exception as e:
            print(f"Error getting popular businesses: {e}")
            return None


    def get_successful_businesses_by_zipcode(self, zip_code):
        sql_str = f"""SELECT name, review_count, numcheckins FROM business WHERE zipcode = '{zip_code}' ORDER BY review_count DESC, numcheckins DESC"""
        try:
            result = self.executeQuery(sql_str)
            return result
        except Exception as e:
            print(f"Error getting successful businesses: {e}")
            return None


    def on_refreshButton_clicked(self):
        zip_code = self.ui.zipcode.selectedItems()[0].text()

        if zip_code:
            # Update the Popular_bus table
            popular_businesses = self.get_popular_businesses_by_zipcode(zip_code)
            self.display_popular_businesses(popular_businesses)

            # Update the Successful_bus table
            successful_businesses = self.get_successful_businesses_by_zipcode(zip_code)
            self.display_successful_businesses(successful_businesses)





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Milestone3()
    window.show()
    sys.exit(app.exec())