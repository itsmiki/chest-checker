import sys
from typing_extensions import ParamSpecArgs
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QLayout, QMainWindow, QSizePolicy, QStyle, QStyleFactory, QTableWidget, QTableWidgetItem, QWidget, QLineEdit, QTableView, QHeaderView, QPushButton, QGridLayout, QLabel, QToolButton, QVBoxLayout, QFormLayout
from PyQt5.QtCore import QObject, QSize, QThread, Qt, QSortFilterProxyModel, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPalette, QPixelFormat, QStandardItemModel, QStandardItem, QColor, QPixmap, QIcon, QWindow
from psutil import Error
from functions_api import get_chest_info, get_encryptedSummonerId, translate_id_to_champion_name
from functions_request import get_champions_owned, get_pickable_champions_aram, get_summoner_icon_id, get_summoner_name
from functions_other import check_if_LeagueClient_is_active, find_LoL_path, get_port_and_password
from functions_request import check_if_aram_lobby
import time, random, json
import urllib
import qdarkstyle

class Checking_Connection_Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(bool)

    def run(self):
        while(1):
            response = check_if_LeagueClient_is_active()
            self.progress.emit(response)
            time.sleep(2)
    
    def stop(self):
        self.is_killed = True
        

class Changing_Layout_Worker(QObject):
    finished = pyqtSignal()

    def run(self, MainWindow):
        if check_if_LeagueClient_is_active() == True:
            MainWindow.clearlayout(MainWindow.supermainLayout)
            MainWindow.initUI_online()
            MainWindow.connection_button.setText('Connected')
            MainWindow.connection_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; color: green')
            MainWindow.connection_button.setDisabled(True)
        else:
            MainWindow.clearlayout(MainWindow.supermainLayout)
            MainWindow.initUI_offline()
            MainWindow.connection_button.setText('Client not active'),
            MainWindow.connection_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; color: red'),
            MainWindow.connection_button.setDisabled(True)
            QTimer.singleShot(2000, lambda : MainWindow.base_style_connection_button())
        
        QTimer.singleShot(6000, lambda : self.finished.emit())


class MainWindow(QWidget):
    switch_window = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        f = open('config', 'r')
        self.config = json.loads(f.read())
        self.temp_config = {'port': '', 'password': '', 'connection_button_state': ''}

        # print(check_if_LeagueClient_is_active())
        self.supermainLayout = QHBoxLayout()
        self.supermainLayout.setContentsMargins(0, 0, 0, 0)
        # self.setStyleSheet('background-color: #1e1e1e')

        self.initUI_offline()
        self.lastInfo = False

        self.mainCheckingConnectionThread = QThread()
        self.Checking_Connection_Worker = Checking_Connection_Worker()

        self.Checking_Connection_Worker.moveToThread(self.mainCheckingConnectionThread)
        
        self.mainCheckingConnectionThread.started.connect(self.Checking_Connection_Worker.run)
        self.Checking_Connection_Worker.finished.connect(self.mainCheckingConnectionThread.quit)
        self.Checking_Connection_Worker.finished.connect(self.Checking_Connection_Worker.deleteLater)
        self.mainCheckingConnectionThread.finished.connect(self.mainCheckingConnectionThread.deleteLater)
        self.Checking_Connection_Worker.progress.connect(self.reportProgress)

        self.mainCheckingConnectionThread.start()

    def reportProgress(self, info):

        if info == True and self.lastInfo == True:
            pass
            # print('Was True is True')
        elif info == False and self.lastInfo == False:
            pass
            # print('Was False is False')

        elif info == True and self.lastInfo == False:
            pass
            # print('Was False is True')
            # self.clearlayout(self.supermainLayout)
            # self.initUI_online()
        elif info == False and self.lastInfo == True:
            # print('Was True is False')
            self.label_status.setText('Offline')
            self.onoffline_pixmap = QPixmap('offline.png')
            self.pixmap1 = self.onoffline_pixmap.scaled(17, 17)
            self.label_onoffline.setPixmap(self.pixmap1)
            self.base_style_connection_button()
        elif self.lastInfo == -1:
            pass

        self.lastInfo = info
    
    def clearlayout(self, layout: QLayout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearlayout(item.layout())

    def connect_to_client(self):
        if check_if_LeagueClient_is_active() == True:
            self.config['path'] = find_LoL_path() # do ulepszenia
            self.temp_config['port'], self.temp_config['password'] = get_port_and_password(self.config['path']) 
            self.clearlayout(self.supermainLayout)
            self.initUI_online()
            self.connection_button.setText('Connected')
            self.connection_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; color: green')
            self.connection_button.setDisabled(True)
        else:
            self.clearlayout(self.supermainLayout)
            self.initUI_offline()
            self.connection_button.setText('Client not active'),
            self.connection_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; color: red'),
            self.connection_button.setDisabled(True)
            QTimer.singleShot(2000, lambda : self.base_style_connection_button())


    
    def connecting_style_connection_button(self):
        self.connection_button.setText('Connecting...')
        self.connection_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; color: #86c5da')
        self.connection_button.setDisabled(True)
    
    def base_style_connection_button(self):
        self.connection_button.setText('Connect'),
        self.connection_button.setStyleSheet(self.get_styleSheet('20px_button')),
        self.connection_button.setDisabled(False)


    def initUI_offline(self):
        self.resize(1000, 600)
        self.setWindowTitle('ChestChecker')
        
        self.mainFrame = QFrame(self)
        self.supermainLayout.addWidget(self.mainFrame)

        self.mainLayout = QGridLayout(self.mainFrame)
        self.mainLayout.setObjectName('MainLayout')

        self.create_sidebar_panel()

        self.create_champion_table(False)

        self.create_connection_panel(False)

        self.setLayout(self.supermainLayout)



    def initUI_online(self):    
        self.resize(1000, 600)
        self.setWindowTitle('ChestChecker')
        
        self.mainFrame = QFrame(self)
        self.supermainLayout.addWidget(self.mainFrame)

        self.mainLayout = QGridLayout(self.mainFrame)
        self.mainLayout.setObjectName('MainLayout')

        self.create_champion_table(True)

        self.create_sidebar_panel()

        self.create_connection_panel(True)
        
        self.setLayout(self.supermainLayout)
        
        # self.mainFrame.setEnabled(False)
    
    def switch(self):
        self.Checking_Connection_Worker.stop()
        self.switch_window.emit()
        self.close()

    def create_champion_table(self, is_online):
        if is_online == True:
            encrypted_summonerId = get_encryptedSummonerId('eun1', get_summoner_name(self.temp_config['port'], self.temp_config['password']))
            result = get_chest_info('eun1', encrypted_summonerId)
            i = 0

            champions_owned = get_champions_owned(self.temp_config['port'], self.temp_config['password'])
            
            champions_owned_ids = []
            for row in champions_owned:
                champions_owned_ids.append(row['id'])
            
            # label1 = QLabel('Champion')
            # label1.setStyleSheet('color: #cccccc; background-color: #333333')

            model = QStandardItemModel(len(champions_owned_ids), 2)
            model.setHorizontalHeaderLabels(['Champion', 'Chest'])
            # model.setHeaderData(0, Qt.Horizontal, 'Champion')

            for row in result:
                champion = QStandardItem(str(row['championName']))
                champion.setFlags(Qt.ItemIsEnabled)
                
                if row['chestGranted'] == False and int(row['championId']) in champions_owned_ids:
                    champions_owned_ids.remove(int(row['championId']))
                    chest = QStandardItem('Available')
                    chest.setFlags(Qt.ItemIsEnabled)
                    model.setItem(i, 1, chest)
                    model.item(i, 1).setBackground(QColor(152, 251, 152))
                    model.setItem(i, 0, champion)
                    # model.item(i, 0).setForeground(QColor(204, 204, 204)) ##
                    i = i + 1 
                elif row['chestGranted'] == True and int(row['championId']) in champions_owned_ids:
                    champions_owned_ids.remove(int(row['championId']))
                    chest = QStandardItem('Granted')
                    chest.setFlags(Qt.ItemIsEnabled)
                    model.setItem(i, 1, chest)
                    model.item(i, 1).setBackground(QColor(199, 81, 80))
                    model.setItem(i, 0, champion)
                    # model.item(i, 0).setForeground(QColor(204, 204, 204)) ##
                    i = i + 1
            
            for element in champions_owned_ids:
                champion = QStandardItem(next((item for item in champions_owned if item["id"] == element), None)['name'])
                chest = QStandardItem('Available')
                champion.setFlags(Qt.ItemIsEnabled)
                chest.setFlags(Qt.ItemIsEnabled)
                model.setItem(i, 1, chest)
                model.item(i, 1).setBackground(QColor(152, 251, 152))
                model.setItem(i, 0, champion)
                # model.item(i, 0).setForeground(QColor(204, 204, 204)) ##
                i = i + 1
        
        if is_online == False:
            model = QStandardItemModel(15, 2)
            model.setHorizontalHeaderLabels(['Champion', 'Chest'])
            pass


        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(-1)
        
        self.find_label = QLabel('Find:')
        self.find_label.setStyleSheet(self.get_styleSheet('20px_label')) ##
        self.mainLayout.addWidget(self.find_label, 0, 3, 1, 1)

        self.search_field = QLineEdit()          
        self.search_field.setStyleSheet(self.get_styleSheet('line_edit')) ##
        self.search_field.textChanged.connect(filter_proxy_model.setFilterRegExp)
        self.mainLayout.addWidget(self.search_field, 0, 4, 1, 8)

        def click_button(action):
            if(action == 'available'):
                filter_proxy_model.setFilterFixedString('Available')
            elif(action == 'granted'):
                filter_proxy_model.setFilterFixedString('Granted')
            elif(action == 'all'):
                filter_proxy_model.setFilterRegularExpression('.+')
            return
            
        self.btn1 = QPushButton("Show All")
        self.btn2 = QPushButton("Show Granted Only")
        self.btn3 = QPushButton("Show Available Only")

        self.btn1.setStyleSheet(self.get_styleSheet('16px_button')) ##
        self.btn2.setStyleSheet(self.get_styleSheet('16px_button')) ##
        self.btn3.setStyleSheet(self.get_styleSheet('16px_button')) ##

        self.btn1.clicked.connect(lambda: click_button('all'))
        self.btn2.clicked.connect(lambda: click_button('granted'))
        self.btn3.clicked.connect(lambda: click_button('available'))

        self.mainLayout.addWidget(self.btn1, 1, 3, 1, 3)
        self.mainLayout.addWidget(self.btn2, 1, 6, 1, 3)
        self.mainLayout.addWidget(self.btn3, 1, 9, 1, 3)

        self.table = QTableView()
        self.table.setStyleSheet('font-size: 24px; font-family: Century Gothic;')
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setStyleSheet(self.get_styleSheet('table_header'))
        self.table.horizontalHeader().setStyleSheet(self.get_styleSheet('table_header'))
        self.table.setModel(filter_proxy_model)
        
        self.mainLayout.addWidget(self.table, 2, 3, 1, 9)



    def create_sidebar_panel(self):
        # self.changingLayoutThread = QThread()
        # self.changingLayoutWorker = Changing_Layout_Worker()

        # self.changingLayoutWorker.moveToThread(self.changingLayoutThread)
        
        # self.changingLayoutThread.started.connect(lambda: self.changingLayoutWorker.run)
        # self.changingLayoutWorker.finished.connect(self.changingLayoutThread.quit)
        # self.changingLayoutWorker.finished.connect(self.changingLayoutWorker.deleteLater)
        # self.changingLayoutThread.finished.connect(self.changingLayoutThread.deleteLater)


        self.sidebarLayout = QFormLayout()

        self.connection_button = QPushButton('Connect')
        self.connection_button.clicked.connect(lambda: (
                                                self.connecting_style_connection_button(),
                                                QTimer.singleShot(100, lambda : self.connect_to_client())
                                                ))
        self.connection_button.setStyleSheet(self.get_styleSheet('20px_button')) ##
        self.sidebarLayout.addWidget(self.connection_button)
        
        self.darkmode_button = QPushButton(self.get_styleSheet('lightmode_button_text'))
        self.darkmode_button.clicked.connect(self.change_theme)
        self.darkmode_button.setStyleSheet(self.get_styleSheet('20px_button')) ##
        self.sidebarLayout.addWidget(self.darkmode_button)

        self.labelx = QLabel()
        self.labelx.setStyleSheet('border: 1px solid gray')
        self.labelx.setFixedHeight(1)
        
        self.sidebarLayout.addWidget(self.labelx)

        self.aram_button = QPushButton('ARAM Lobby')
        self.aram_button.clicked.connect(self.switch)
        self.aram_button.setStyleSheet(self.get_styleSheet('20px_button')) ##
        self.sidebarLayout.addWidget(self.aram_button)

        self.allchampions_button = QPushButton(' All Champions')
        self.allchampions_button.setStyleSheet(self.get_styleSheet('20px_button')) ##
        self.sidebarLayout.addWidget(self.allchampions_button)

        self.mainLayout.addLayout(self.sidebarLayout, 0, 0, 3, 3)
    
    def change_theme(self):
        if self.config['theme'] == 'light':
            self.dark_theme() 
            self.darkmode_button.setText('Light Mode')
            self.config['theme'] = 'dark'
        else:
            self.light_theme() 
            self.darkmode_button.setText('Dark Mode') 
            self.config['theme'] = 'light'

    def get_styleSheet(self, element):
        self.styles = {
            'dark': {
                '16px_button': 'font-family: Century Gothic; font-size: 16px; background-color: #333333; color: #cccccc',
                'main_background': 'background-color: #1e1e1e',
                'line_edit': 'font-size: 24px; font-family: Century Gothic; height: 40px; color: #cccccc; border: 1px solid #cccccc;',
                '20px_label': 'font-size: 20px; font-family: Century Gothic; height: 30px; color: #cccccc;',
                '18px_label': 'font-family: Century Gothic; font-size: 18px; color: #cccccc',
                '11px_label': 'font-family: Century Gothic; font-size: 11px; color: #cccccc',
                'table_header': 'background-color: #333333; color: #cccccc',
                '20px_button': 'font-size: 20px; font-family: Century Gothic; height: 30px; background-color: #333333; color: #cccccc',
                'connectionlayout_bg': 'background-color: #333333;',
                'lightmode_button_text': 'Light Mode',
            },
            'light': {
                '16px_button': 'font-family: Century Gothic; font-size: 16px;',
                'main_background': '',
                'line_edit': 'font-size: 24px; font-family: Century Gothic; height: 40px;',
                '20px_label': 'font-size: 20px; font-family: Century Gothic; height: 30px;',
                '18px_label': 'font-family: Century Gothic; font-size: 18px;',
                '11px_label': 'font-family: Century Gothic; font-size: 11px;',
                'table_header': '',
                '20px_button': 'font-size: 20px; font-family: Century Gothic; height: 30px;',
                'connectionlayout_bg': 'background-color: #fafafa;',
                'lightmode_button_text': 'Dark Mode',
            }
        }
        return self.styles[self.config['theme']][element]

    def dark_theme(self):   
        self.setStyleSheet('background-color: #1e1e1e')

        self.find_label.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; color: #cccccc;') ##
        self.search_field.setStyleSheet('font-size: 24px; font-family: Century Gothic; height: 40px; color: #cccccc; border: 1px solid #cccccc;')
        self.btn1.setStyleSheet('font-family: Century Gothic; font-size: 16px; background-color: #333333; color: #cccccc') ##
        self.btn2.setStyleSheet('font-family: Century Gothic; font-size: 16px; background-color: #333333; color: #cccccc') ##
        self.btn3.setStyleSheet('font-family: Century Gothic; font-size: 16px; background-color: #333333; color: #cccccc') ##

        self.table.verticalHeader().setStyleSheet('background-color: #333333; color: #cccccc')
        self.table.horizontalHeader().setStyleSheet('background-color: #333333; color: #cccccc')

        self.connection_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; background-color: #333333; color: #cccccc') ##
        self.darkmode_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; background-color: #333333; color: #cccccc') ##
        self.aram_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; background-color: #333333; color: #cccccc') ##
        self.allchampions_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px; background-color: #333333; color: #cccccc') ##

        self.frame_connectionLayout.setStyleSheet("background-color: #333333;")
        self.label_summonerName.setStyleSheet('font-family: Century Gothic; font-size: 18px; color: #cccccc')
        self.label_status.setStyleSheet('font-family: Century Gothic; font-size: 11px; color: #cccccc')
        self.chestNumber_label.setStyleSheet('font-family: Century Gothic; font-size: 11px; color: #cccccc; font-weight: bold')

    def light_theme(self):
        self.setStyleSheet('')

        self.find_label.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;') ##
        self.search_field.setStyleSheet('font-size: 24px; font-family: Century Gothic; height: 40px;')
        self.btn1.setStyleSheet('font-family: Century Gothic; font-size: 16px; ') ##
        self.btn2.setStyleSheet('font-family: Century Gothic; font-size: 16px; ') ##
        self.btn3.setStyleSheet('font-family: Century Gothic; font-size: 16px; ') ##

        self.table.verticalHeader().setStyleSheet('')
        self.table.horizontalHeader().setStyleSheet('')

        self.connection_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;') ##
        self.darkmode_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;') ##
        self.aram_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;') ##
        self.allchampions_button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;') ##

        self.frame_connectionLayout.setStyleSheet("background-color: #fafafa;")
        self.label_summonerName.setStyleSheet('font-family: Century Gothic; font-size: 18px;')
        self.label_status.setStyleSheet('font-family: Century Gothic; font-size: 11px;')
        self.chestNumber_label.setStyleSheet('font-family: Century Gothic; font-size: 11px; font-weight: bold')


    def create_connection_panel(self, is_online):
        if is_online == True:
            self.label_summonerName = QLabel(get_summoner_name(self.temp_config['port'], self.temp_config['password']))
            self.label_status = QLabel('Online')
            self.onoffline_pixmap = QPixmap('online.png')

            url = 'http://ddragon.leagueoflegends.com/cdn/11.14.1/img/profileicon/'+ str(get_summoner_icon_id(self.temp_config['port'], self.temp_config['password'])) +'.png'
            data = urllib.request.urlopen(url).read()
            self.summonerIcon_pixmap = QPixmap()
            self.summonerIcon_pixmap.loadFromData(data)

        if is_online == False:
            self.label_summonerName = QLabel('Summoner')#
            self.label_status = QLabel('Offline') #
            self.onoffline_pixmap = QPixmap('offline.png') #
            self.summonerIcon_pixmap = QPixmap('icon.png') #
            
        
        self.frame_connectionLayout = QFrame(self)
        self.frame_connectionLayout.setStyleSheet(self.get_styleSheet('connectionlayout_bg')) ## background-color: #fafafa;

        self.connectionLayout = QGridLayout(self.frame_connectionLayout)
        self.label_summonerName.setFrameStyle(0)
        self.label_summonerName.setStyleSheet(self.get_styleSheet('18px_label')) ##
        self.connectionLayout.addWidget(self.label_summonerName, 1, 2, 1, 8)

        self.label_status.setStyleSheet(self.get_styleSheet('11px_label'))
        self.connectionLayout.addWidget(self.label_status, 2, 3, 1, 1)

        self.label_onoffline = QLabel()
        self.pixmap1 = self.onoffline_pixmap.scaled(17, 17)
        self.label_onoffline.setPixmap(self.pixmap1)
        self.connectionLayout.addWidget(self.label_onoffline, 2, 2, 1, 1)

        self.label_summonerIcon = QLabel()
        self.pixmap1 = self.summonerIcon_pixmap.scaled(45, 45)
        self.label_summonerIcon.setPixmap(self.pixmap1)
        self.connectionLayout.addWidget(self.label_summonerIcon, 1, 0, 2, 2)

        self.chest_label = QLabel()
        self.chestNumber_label = QLabel('TODO')
        self.chestNumber_label.setStyleSheet(self.get_styleSheet('11px_label') + '; font-weight: bold')
        
        self.chest_pixmap = QPixmap('Hextech_Crafting_Chest.png')

        self.chest_pixmap = self.chest_pixmap.scaled(17, 17)

        self.chest_label.setPixmap(self.chest_pixmap)

        self.connectionLayout.addWidget(self.chest_label, 2, 5, 1, 1)
        self.connectionLayout.addWidget(self.chestNumber_label, 2, 6, 1, 1)


        self.mainLayout.addWidget(self.frame_connectionLayout, 0, 0, 3, 3, alignment = Qt.AlignBottom)





class ARAMWindow(QWidget):
    switch_window = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.config = {'theme': 'light',}
        self.temp_config = {'port': '62342', 'password': '_VVDokVR_mW-0igYELgJBw'}
        self.initUI()

    def initUI(self):
        self.resize(1000, 600)
        self.setWindowTitle('ChestChecker')
        self.mainLayout = QGridLayout()

        self.champions_owned_ids = []

        champions_owned = get_champions_owned(self.temp_config['port'], self.temp_config['password'])
        
        for row in champions_owned:
            self.champions_owned_ids.append(row['id'])

        # print(self.champions_owned_ids)

        encrypted_summonerId = get_encryptedSummonerId('eun1', get_summoner_name(self.temp_config['port'], self.temp_config['password']))
        self.chest_info = get_chest_info('eun1', encrypted_summonerId)

        # print(self.chest_info)


        self.timer = QTimer(self, interval=2000)
        self.timer.timeout.connect(self.on_update)
        self.timer.start()

        self.sidebarLayout = QFormLayout()
# ======================================
        # self.label_summonerName = QLabel(get_summoner_name(self.temp_config['port'], self.temp_config['password']))
        # self.label_status = QLabel('Online')
        # self.onoffline_pixmap = QPixmap('online.png')

        # url = 'http://ddragon.leagueoflegends.com/cdn/11.14.1/img/profileicon/'+ str(get_summoner_icon_id(self.temp_config['port'], self.temp_config['password'])) +'.png'
        # data = urllib.request.urlopen(url).read()
        # self.summonerIcon_pixmap = QPixmap()
        # self.summonerIcon_pixmap.loadFromData(data)

            
        
        # self.frame_connectionLayout = QFrame(self)
        # self.frame_connectionLayout.setStyleSheet(self.get_styleSheet('connectionlayout_bg')) ## background-color: #fafafa;

        # self.connectionLayout = QGridLayout(self.frame_connectionLayout)
        # self.label_summonerName.setFrameStyle(0)
        # self.label_summonerName.setStyleSheet(self.get_styleSheet('18px_label')) ##
        # self.connectionLayout.addWidget(self.label_summonerName, 1, 2, 1, 8)

        # self.label_status.setStyleSheet(self.get_styleSheet('11px_label'))
        # self.connectionLayout.addWidget(self.label_status, 2, 3, 1, 1)

        # self.label_onoffline = QLabel()
        # self.pixmap1 = self.onoffline_pixmap.scaled(17, 17)
        # self.label_onoffline.setPixmap(self.pixmap1)
        # self.connectionLayout.addWidget(self.label_onoffline, 2, 2, 1, 1)

        # self.label_summonerIcon = QLabel()
        # self.pixmap1 = self.summonerIcon_pixmap.scaled(45, 45)
        # self.label_summonerIcon.setPixmap(self.pixmap1)
        # self.connectionLayout.addWidget(self.label_summonerIcon, 1, 0, 2, 2)

        # self.chest1_label = QLabel()
        # self.chest2_label = QLabel('TODO')
        # self.chest2_label.setStyleSheet(self.get_styleSheet('11px_label') + 'font-weight: bold')
        # # self.chest3_label = QLabel()
        # # self.chest4_label = QLabel()
        
        # self.chest1_pixmap = QPixmap('Hextech_Crafting_Chest.png')
        # # self.chest2_pixmap = QPixmap('chest.png')
        # # self.chest3_pixmap = QPixmap('chest_unavailable.png')
        # # self.chest4_pixmap = QPixmap('chest_unavailable.png')
        
        # self.chest1_pixmap = self.chest1_pixmap.scaled(17, 17)
        # # self.chest2_pixmap = self.chest2_pixmap.scaled(45, 45)
        # # self.chest3_pixmap = self.chest3_pixmap.scaled(45, 45)
        # # self.chest4_pixmap = self.chest4_pixmap.scaled(45, 45)

        # self.chest1_label.setPixmap(self.chest1_pixmap)
        # # self.chest2_label.setPixmap(self.chest2_pixmap)
        # # self.chest3_label.setPixmap(self.chest3_pixmap)
        # # self.chest4_label.setPixmap(self.chest4_pixmap)

        # self.connectionLayout.addWidget(self.chest1_label, 2, 5, 1, 1)
        # self.connectionLayout.addWidget(self.chest2_label, 2, 6, 1, 1)
        # # self.connectionLayout.addWidget(self.chest3_label, 0, 4, 1, 2)
        # # self.connectionLayout.addWidget(self.chest4_label, 0, 6, 1, 2)

        # self.mainLayout.addWidget(self.frame_connectionLayout, 0, 0, 3, 3, alignment = Qt.AlignBottom)
# ======================================
        self.button = QPushButton('ARAM Lobby')
        self.button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;')
        self.sidebarLayout.addWidget(self.button)

        self.button = QPushButton('All Champions')
        self.button.clicked.connect(self.switch)
        self.button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;')
        self.sidebarLayout.addWidget(self.button)

        self.model = QStandardItemModel(15, 2)
        self.model.setHorizontalHeaderLabels(['Champion', 'Chest'])
        self.table = QTableView()
        self.table.setStyleSheet('font-size: 24px; font-family: Century Gothic')
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setModel(self.model)

        self.mainLayout.addWidget(self.table, 0, 3, 3, 9)
        self.setLayout(self.mainLayout)

        self.mainLayout.addLayout(self.sidebarLayout, 0, 0, 3, 3)


    def on_update(self):
        if check_if_aram_lobby(self.temp_config['port'], self.temp_config['password']) == True:    #zmienić na true
            try:
                self.mainLayout.removeWidget(self.table)
            except:
                pass

            try:
                self.mainLayout.removeWidget(self.label)
            except:
                pass
            
            self.model = QStandardItemModel(15, 2)
            self.model.setHorizontalHeaderLabels(['Champion', 'Chest'])

            champion_ids = get_pickable_champions_aram(self.temp_config['port'], self.temp_config['password'])
            champion_names = translate_id_to_champion_name(champion_ids)
            # print(champion_names)

            for i in range (len(champion_ids)):
                if int(champion_ids[i]) in self.champions_owned_ids:
                    champion = QStandardItem(champion_names[i])
                    champion.setFlags(Qt.ItemIsEnabled)
                    for j in range (len(self.chest_info)):
                        if self.chest_info[j]['championId'] == champion_ids[i]:
                            chest = self.chest_info[j]['chestGranted']
                            break
                        else:
                            chest = False
                    
                    if chest == False:
                        chest = QStandardItem('Available')
                        chest.setFlags(Qt.ItemIsEnabled)
                        self.model.setItem(i, 1, chest)
                        self.model.item(i, 1).setBackground(QColor(152, 251, 152))
                        self.model.setItem(i, 0, champion)
                    else:
                        chest = QStandardItem('Granted')
                        chest.setFlags(Qt.ItemIsEnabled)
                        self.model.setItem(i, 1, chest)
                        self.model.item(i, 1).setBackground(QColor(199, 81, 80))
                        self.model.setItem(i, 0, champion)
                else:
                    champion = QStandardItem(champion_names[i])
                    chest = QStandardItem('Not Owned')
                    champion.setFlags(Qt.ItemIsEnabled)
                    chest.setFlags(Qt.ItemIsEnabled)
                    self.model.setItem(i, 1, chest)
                    self.model.item(i, 1).setBackground(QColor(220,220,220))
                    self.model.setItem(i, 0, champion)
                


            self.table = QTableView()
            self.table.setStyleSheet('font-size: 24px; font-family: Century Gothic')
            self.table.verticalHeader().setDefaultSectionSize(40)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.setModel(self.model)

            self.mainLayout.addWidget(self.table, 0, 3, 3, 9)
            self.setLayout(self.mainLayout)

        else:
            try:
                self.mainLayout.removeWidget(self.label)
            except:
                try:
                    pass
                    #self.self.mainLayout.removeWidget(self.table)
                except:
                    pass


            # self.label = QLabel('Waiting for ARAM game to begin.')
            # self.label.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;')
            # self.self.mainLayout.addWidget(self.label)
            self.setLayout(self.mainLayout)
    
    def switch(self):
        self.timer.stop()
        self.switch_window.emit()
        self.close()


class SetupWindow(QWidget):
    switch_window = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('Setup')

        layout = QGridLayout()

        self.label = QLabel('Summoner Name:')
        self.label.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;')
        layout.addWidget(self.label, 0, 0, 1, 1)

        self.line_edit = QLineEdit()
        self.line_edit.setText(get_summoner_name(self.temp_config['port'], self.temp_config['password']))
        self.line_edit.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;')
        layout.addWidget(self.line_edit, 0, 1, 1, 1)


        self.button = QPushButton('Go')
        self.button.clicked.connect(self.switch)
        self.button.setStyleSheet('font-size: 20px; font-family: Century Gothic; height: 30px;')
        layout.addWidget(self.button, 1, 0, 1, 2)

        self.setLayout(layout)

    def switch(self):
        self.switch_window.emit(self.line_edit.text())
        self.close()


class Controller:

    def __init__(self):
        pass

    def show_login(self):
        self.login = SetupWindow()
        self.login.switch_window.connect(self.show_main)
        self.login.show()

    def show_main(self):
        self.mainwindow = MainWindow()
        self.mainwindow.switch_window.connect(self.show_ARAM)
        self.mainwindow.show()

    def show_ARAM(self):
        self.aramwindow = ARAMWindow()
        self.mainwindow.close()
        self.aramwindow.switch_window.connect(self.show_main)
        self.aramwindow.show()


def main():
    app = QApplication(sys.argv)
    # f = open('style.qss', 'r')
    # style = f.read()
    # print(QStyleFactory.keys())
    # app.setStyleSheet(style)
    app.setStyle(QStyleFactory.create('Fusion')) # won't work on windows style.
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    controller = Controller()
    controller.show_main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


    
    # app = QApplication(sys.argv)
    # demo = ARAMWindow()
    # demo.show()
    # sys.exit(app.exec_())


