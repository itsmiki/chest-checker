import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QTableView, QHeaderView, QPushButton, QGridLayout, QLabel
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from functions_api import get_chest_info, get_encryptedSummonerId
from functions_lcu import get_champions_owned

class MainWindow(QWidget):
    def __init__(self, summonerName):
        QWidget.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle('ChestChecker')
        mainLayout = QGridLayout()

        miki = get_encryptedSummonerId('eun1', summonerName)
        result = get_chest_info('eun1', miki)
        i = 0

        champions_owned = []
        get_champions_owned(champions_owned)
        
        champions_owned_ids = []
        for row in champions_owned:
            champions_owned_ids.append(row['id'])

        model = QStandardItemModel(len(champions_owned_ids), 2)
        model.setHorizontalHeaderLabels(['Champion', 'Chest'])

        # for row, company in enumerate(companies):
        #     item = QStandardItem(company)
        #     model.setItem(row, 0, item)

        # print(champions_owned_ids)

        for row in result:
            champion = QStandardItem(str(row['championName']))
            
            if row['chestGranted'] == False and int(row['championId']) in champions_owned_ids:
                champions_owned_ids.remove(int(row['championId']))
                chest = QStandardItem('Available')
                model.setItem(i, 1, chest)
                model.item(i, 1).setBackground(QColor(152, 251, 152))
                model.setItem(i, 0, champion)
                i = i + 1 
            elif row['chestGranted'] == True and int(row['championId']) in champions_owned_ids:
                champions_owned_ids.remove(int(row['championId']))
                chest = QStandardItem('Granted')
                model.setItem(i, 1, chest)
                model.item(i, 1).setBackground(QColor(199, 81, 80))
                model.setItem(i, 0, champion)
                i = i + 1
        
        for element in champions_owned_ids:
            champion = QStandardItem(next((item for item in champions_owned if item["id"] == element), None)['name'])
            chest = QStandardItem('Available')
            model.setItem(i, 1, chest)
            model.item(i, 1).setBackground(QColor(152, 251, 152))
            model.setItem(i, 0, champion)
            i = i + 1




        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(-1)
        
        self.label = QLabel('Find:')
        self.label.setStyleSheet('font-size: 20px; font-family: Courier New; height: 30px;')
        mainLayout.addWidget(self.label, 0, 0, 1, 1)

        search_field = QLineEdit()          
        search_field.setStyleSheet('font-size: 24px; font-family: Courier New; height: 40px;')
        search_field.textChanged.connect(filter_proxy_model.setFilterRegExp)
        mainLayout.addWidget(search_field, 0, 1, 1, 8)

        def click_button(action):
            if(action == 'available'):
                filter_proxy_model.setFilterFixedString('Available')
            elif(action == 'granted'):
                filter_proxy_model.setFilterFixedString('Granted')
            elif(action == 'all'):
                filter_proxy_model.setFilterRegularExpression('.+')
            return
            
        btn1 = QPushButton("Show All")
        btn2 = QPushButton("Show Granted Only")
        btn3 = QPushButton("Show Available Only")

        btn1.setStyleSheet('font-family: Courier New; font-size: 16px')
        btn2.setStyleSheet('font-family: Courier New; font-size: 16px')
        btn3.setStyleSheet('font-family: Courier New; font-size: 16px')

        btn1.clicked.connect(lambda: click_button('all'))
        btn2.clicked.connect(lambda: click_button('granted'))
        btn3.clicked.connect(lambda: click_button('available'))

        mainLayout.addWidget(btn1, 1, 0, 1, 3)
        mainLayout.addWidget(btn2, 1, 3, 1, 3)
        mainLayout.addWidget(btn3, 1, 6, 1, 3)

        table = QTableView()
        table.setStyleSheet('font-size: 24px; font-family: Courier New')
        table.verticalHeader().setDefaultSectionSize(40)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setModel(filter_proxy_model)
        mainLayout.addWidget(table, 2, 0, 1, 9)

        self.setLayout(mainLayout)



class SetupWindow(QWidget):
    switch_window = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('Setup')

        layout = QGridLayout()

        self.label = QLabel('Summoner Name:')
        self.label.setStyleSheet('font-size: 20px; font-family: Courier New; height: 30px;')
        layout.addWidget(self.label, 0, 0, 1, 1)

        self.line_edit = QLineEdit()
        self.line_edit.setStyleSheet('font-size: 20px; font-family: Courier New; height: 30px;')
        layout.addWidget(self.line_edit, 0, 1, 1, 1)


        self.button = QPushButton('Go')
        self.button.clicked.connect(self.switch)
        self.button.setStyleSheet('font-size: 20px; font-family: Courier New; height: 30px;')
        layout.addWidget(self.button, 1, 0, 1, 2)

        self.setLayout(layout)

    def switch(self):
        self.switch_window.emit(self.line_edit.text())

class Controller:

    def __init__(self):
        pass

    def show_login(self):
        self.login = SetupWindow()
        self.login.switch_window.connect(self.show_main)
        self.login.show()

    def show_main(self, text):
        self.window = MainWindow(text)
        self.login.close()
        self.window.show()

def main():
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show_login()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


# app = QApplication(sys.argv)
# demo = MainWindow()
# demo.show()
# sys.exit(app.exec_())
