import sys
import pandas as pd
import numpy as np

from gui.toolsGui import PARAMGUI

from PySide6.QtCore import SIGNAL
from PySide6 import  QtWidgets, QtGui # -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtGui import QColor

import pyqtgraph as pg

pal = QPalette()
pal.setColor(QPalette.Base, QColor(60, 60, 60))
pal.setColor(QPalette.Button, QColor(60, 60, 60))
pal.setColor(QPalette.Text, QColor(255, 255, 255))
pal.setColor(QPalette.WindowText, QColor(255, 255, 255))

palRed = QPalette()
palRed.setColor(QPalette.Base, QColor(60, 60, 60))
palRed.setColor(QPalette.Button, QColor(60, 60, 60))
palRed.setColor(QPalette.Text, QColor(255, 0, 0))
palRed.setColor(QPalette.WindowText, QColor(255, 0, 0))

NPLOTSIZE = 1200

class MYPLOT(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('p2PilotePlot.py')
        
           
        self.jsonConf = PARAMGUI(project= "Pilote")
       
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        

        self.createP2PiloteGroupBox()

        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.addWidget(self.P2PiloteGroupBox,1, 1)
        
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.centralWidget.setLayout(self.mainLayout)

        self.connect(self.btnLogFile, SIGNAL("clicked()"),self.selectLogFile)


      
    def closeEvent(self, event):        

        self.shutdown()
        
    
    def runtimerPlotrefresh(self):
        if self.enRefreshGraph == 1:
            self.appendChrono() 
            self.enRefreshGraph = 0
            
    def clearChrono(self):
        try:
            self.linemV1.clear()
            self.linemV2.clear()
            self.linemV3.clear()
            self.linemV4.clear()
            self.linemV5.clear()
            self.linemV6.clear()
            
            self.linemI1.clear()
            self.linemI2.clear()
            self.linemI3.clear()
            self.linemI4.clear()
            self.linemI5.clear()
            self.linemI6.clear()
        except:
            None
    def appendChrono(self):
        try:
                #self.appendTabChrono()
            self.clearChrono()
            
            self.linemVPS.setData(x=self.time, y=self.tabmVPS) 
            self.linemIPS.setData(x=self.time, y=self.tabmIPS) 
            
            self.linemV1.setData(x=self.time, y=self.tabmV1)
            self.linemV2.setData(x=self.time, y=self.tabmV2)
            self.linemV3.setData(x=self.time, y=self.tabmV3)
            self.linemV4.setData(x=self.time, y=self.tabmV4)
            self.linemV5.setData(x=self.time, y=self.tabmV5)
            self.linemV6.setData(x=self.time, y=self.tabmV6)     
    
            self.linemI1.setData(x=self.time, y=self.tabmI1)
            self.linemI2.setData(x=self.time, y=self.tabmI2)
            self.linemI3.setData(x=self.time, y=self.tabmI3)
            self.linemI4.setData(x=self.time, y=self.tabmI4)
            self.linemI5.setData(x=self.time, y=self.tabmI5)
            self.linemI6.setData(x=self.time, y=self.tabmI6)
        except:
            self.clearChrono()

                               
               
        
    
    def selectLogFile(self):
        file_path, _  = QtWidgets.QFileDialog.getOpenFileName(self, "Open Log File", "/home/jana", "Image Files (*.csv *.log)")
        if file_path:
            self.status_label.setText(f"Fichier sélectionné : {file_path}")
            try:
                # Lecture du fichier CSV avec pandas
                # sep=';' indique que le séparateur est le point-virgule
                # header=0 indique que la première ligne est l'en-tête (indice 0)
                df = pd.read_csv(file_path, sep=';', header=0)

                self.status_label.setText(f"Données du fichier '{file_path}' chargées avec succès.")
                print("\n--- Aperçu des 5 premières lignes des données ---")
                print(df.head())

                print("\n--- Informations sur les colonnes ---")
                print(df.info())
                #self.clearTabmList()
                self.plotRange = len(df)
                df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
                df['unix_timestamp'] = df['time'].apply(lambda x: x.timestamp())
                self.time = df['unix_timestamp'].tolist()
                # Maintenant, time_unix_timestamps contient les valeurs numériques pour l'axe X
                # et data_y contient les valeurs pour l'axe Y.
                tableau_numpy = np.array(df["VPS(V)"].astype(float).tolist())
                tableau_divise = tableau_numpy * 1000.0
                self.tabmVPS = tableau_divise.tolist()
                
                tableau_numpy = np.array(df["IPS(A)"].astype(float).tolist())
                tableau_divise = tableau_numpy * 1000.0
                self.tabmIPS = tableau_divise.tolist()

                self.tabmV1 = df["V1(mV)"].astype(float).tolist()
                self.tabmV2 = df["V2(mV)"].astype(float).tolist()
                self.tabmV3 = df["V3(mV)"].astype(float).tolist()
                self.tabmV4 = df["V4(mV)"].astype(float).tolist()
                self.tabmV5 = df["V5(mV)"].astype(float).tolist()
                self.tabmV6 = df["V6(mV)"].astype(float).tolist()
                self.tabmI1 = df["I1(mA)"].astype(float).tolist()
                self.tabmI2 = df["I2(mA)"].astype(float).tolist()
                self.tabmI3 = df["I3(mA)"].astype(float).tolist()
                self.tabmI4 = df["I4(mA)"].astype(float).tolist()
                self.tabmI5 = df["I5(mA)"].astype(float).tolist()
                self.tabmI6 = df["I6(mA)"].astype(float).tolist()
                self.appendChrono()
                
                # --- Ajouter les régions de surbrillance pour l'état binaire ---
                self.highlight_regions = []
                self.binary_state = df["polarState"].astype(float).tolist()
                self.add_binary_state_highlights()
                
                print(self.time)
                # Ici, vous pouvez ajouter d'autres traitements sur le DataFrame 'df'
                # Par exemple, sauvegarder dans un autre format, analyser, etc.
                # Exemple: Sauvegarder dans un nouveau fichier CSV avec des virgules
                # output_file_path = file_path.replace(".csv", "_processed.csv")
                # df.to_csv(output_file_path, index=False)
                # print(f"\nDonnées traitées sauvegardées dans : {output_file_path}")

            except FileNotFoundError:
                self.status_label.setText("Erreur : Fichier non trouvé.")
            except pd.errors.EmptyDataError:
                self.status_label.setText("Erreur : Le fichier CSV est vide.")
            except pd.errors.ParserError:
                self.status_label.setText("Erreur : Impossible de parser le fichier CSV. Vérifiez le format (séparateur, etc.).")
            except Exception as e:
                self.status_label.setText(f"Une erreur inattendue est survenue : {e}")
        else:
            self.status_label.setText("Aucun fichier sélectionné.")

    def add_binary_state_highlights(self):
        # Supprime les régions existantes pour rafraîchir si nécessaire
        for region in self.highlight_regions:
            self.plot_widget.removeItem(region)
        self.highlight_regions = []

        # Identifier les débuts et fins des périodes d'activité (où binary_state passe de 0 à 1 ou 1 à 0)
        # Ceci est une logique simple, à adapter si votre état est plus complexe
        active_periods = []
        in_active_period = False
        start_index = -1

        for i, state in enumerate(self.binary_state):
            if state == 1 and not in_active_period:
                in_active_period = True
                start_index = i
            elif state == 0 and in_active_period:
                in_active_period = False
                # Utilisez les timestamps Unix pour les limites
                start_ts = self.time[start_index]
                end_ts = self.time[i-1] # Le dernier point actif
                active_periods.append((start_ts, end_ts))
        
        # Si l'état est toujours actif à la fin des données
        if in_active_period:
            start_ts = self.time[start_index]
            end_ts = self.time[-1]
            active_periods.append((start_ts, end_ts))

        # Ajouter chaque période comme un LinearRegionItem
        for start, end in active_periods:
            regionV = pg.LinearRegionItem(
                values=(start, end),
                orientation='vertical',
                brush=pg.mkBrush(49, 140, 231, 20), # Rouge transparent (RGBA)
                pen=pg.mkPen(None) # Pas de bordure pour la région
            )
            # Rendre la région non déplaçable par l'utilisateur si désiré
            regionV.setMovable(False)
            self.plotmV.addItem(regionV)
            self.highlight_regions.append(regionV)
            
            regionA = pg.LinearRegionItem(
                values=(start, end),
                orientation='vertical',
                brush=pg.mkBrush(49, 140, 231, 20), # Rouge transparent (RGBA)
                pen=pg.mkPen(None) # Pas de bordure pour la région
            )
            # Rendre la région non déplaçable par l'utilisateur si désiré
            regionA.setMovable(False)
            self.plotmA.addItem(regionA)
            self.highlight_regions.append(regionA)

        # Assurez-vous que les régions sont derrière la courbe principale
        # plot_widget.plotItem.items() retourne les items dans l'ordre d'ajout.
        # Vous pouvez les réorganiser ou ajouter les régions en premier.
        # Une option plus simple: les ajouter comme "background items"
        # self.plot_widget.plotItem.add_item_to_background(region) - ceci n'existe pas directement
        # Par défaut, les éléments sont ajoutés par-dessus. Pour les mettre en arrière-plan,
        # il faut manipuler l'ordre des éléments dans la ViewBox.
        # Une astuce est d'ajouter les régions avant la courbe principale.
        # Ou utiliser setZValue() pour les envoyer derrière (valeur négative)
        # Par exemple, pour les régions: region.setZValue(-100)
        # Et pour la courbe: self.curve.setZValue(0)
        for regionV in self.highlight_regions:
            regionV.setZValue(-10) # Envoie les régions derrière la courbe
        for regionA in self.highlight_regions:
            regionA.setZValue(-10) # Envoie les régions derrière la courbe

    def createP2PiloteGroupBox(self):
        self.P2PiloteGroupBox = QtWidgets.QGroupBox()
        self.P2PiloteGroupBox.setGeometry(0,0,10,10)
        palette = self.P2PiloteGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.P2PiloteGroupBox.setPalette(palette)    
        mainLayout = QtWidgets.QGridLayout()  
        
        self.btnLogFile = QtWidgets.QPushButton("LogFile")
        self.btnLogFile.setPalette(pal)
        self.btnLogFile.setDefault(True)
        mainLayout.addWidget(self.btnLogFile,0,0)
        
        self.status_label = QtWidgets.QLabel("Cliquez sur le bouton pour sélectionner un fichier CSV.", self)
        self.status_label.setPalette(pal)
        mainLayout.addWidget(self.status_label,0,1)
        
    
        self.plotRange = NPLOTSIZE
        self.plotmV = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.plotmV.setBackground((53, 53, 53))
        
        styles = {"color": "grey", "font-size": "18px"}
        self.plotmV.setLabel("left", "Voltage [mV]", **styles)
        #self.plotmV.setLabel("bottom", "Time [sec]", **styles)
        self.plotmV.addLegend()
        self.plotmV.showGrid(x=True, y=True)
        self.plotmV.setYRange(-3000, 3000)
        self.time = []
        self.clearTabmList(tab=self.time)
        
        pen = pg.mkPen(color=(255, 0, 0))
        self.tabmV1 = []
        self.clearTabmList(tab=self.tabmV1)
        self.linemV1 = self.plotmV.plot(
            self.time,
            self.tabmV1,
            name="V1",
            pen=pen,
            symbol="o",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(0, 255, 0))
        self.tabmV2 = []
        self.clearTabmList(tab=self.tabmV2)
        self.linemV2 = self.plotmV.plot(
            self.time,
            self.tabmV2,
            name="V2",
            pen=pen,
            symbol="t",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(0, 0, 255))
        self.tabmV3 = []
        self.clearTabmList(tab=self.tabmV3)
        self.linemV3 = self.plotmV.plot(
            self.time,
            self.tabmV3,
            name="V3",
            pen=pen,
            symbol="t1",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(255, 0, 255))
        self.tabmV4 = []
        self.clearTabmList(tab=self.tabmV4)
        self.linemV4 = self.plotmV.plot(
            self.time,
            self.tabmV4,
            name="V4",
            pen=pen,
            symbol="t2",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(255, 255, 255))
        self.tabmV5 = []
        self.clearTabmList(tab=self.tabmV5)
        self.linemV5 = self.plotmV.plot(
            self.time,
            self.tabmV5,
            name="V5",
            pen=pen,
            symbol="t3",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(250, 237, 39))
        self.tabmV6 = []
        self.clearTabmList(tab=self.tabmV6)
        self.linemV6 = self.plotmV.plot(
            self.time,
            self.tabmV6,
            name="V6",
            pen=pen,
            symbol="s",
            symbolSize=1,
            symbolBrush="g",
        )        
                
        pen = pg.mkPen(color=(250, 39, 237))
        self.tabmVPS = []
        self.clearTabmList(tab=self.tabmVPS)
        self.linemVPS = self.plotmV.plot(
            self.time,
            self.tabmVPS,
            name="VPS",
            pen=pen,
            symbol="o",
            symbolSize=1,
            symbolBrush="g",
        )
        
        self.plotmA = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.plotmA.setBackground((53, 53, 53))
        pen = pg.mkPen(color=(255, 0, 0))
        styles = {"color": "grey", "font-size": "18px"}
        self.plotmA.setLabel("left", "Current [mA]", **styles)
        self.plotmA.setLabel("bottom", "Time", **styles)
        self.plotmA.addLegend()
        self.plotmA.showGrid(x=True, y=True)
        self.plotmA.setYRange(0, 3000)
        
        pen = pg.mkPen(color=(255, 0, 0))
        self.tabmI1 = []
        self.clearTabmList(tab=self.tabmI1)
        self.linemI1 = self.plotmA.plot(
            self.time,
            self.tabmI1,
            name="I1",
            pen=pen,
            symbol="o",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(0, 255, 0))
        self.tabmI2 = []
        self.clearTabmList(tab=self.tabmI2)
        self.linemI2 = self.plotmA.plot(
            self.time,
            self.tabmI2,
            name="I2",
            pen=pen,
            symbol="t",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(0, 0, 255))
        self.tabmI3 = []
        self.clearTabmList(tab=self.tabmI3)
        self.linemI3 = self.plotmA.plot(
            self.time,
            self.tabmI3,
            name="I3",
            pen=pen,
            symbol="t1",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(255, 0, 255))
        self.tabmI4 = []
        self.clearTabmList(tab=self.tabmI4)
        self.linemI4 = self.plotmA.plot(
            self.time,
            self.tabmI4,
            name="I4",
            pen=pen,
            symbol="t2",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(255, 255, 255))
        self.tabmI5 = []
        self.clearTabmList(tab=self.tabmI5)
        self.linemI5 = self.plotmA.plot(
            self.time,
            self.tabmI5,
            name="I5",
            pen=pen,
            symbol="t3",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(250, 237, 39))
        self.tabmI6 = []
        self.clearTabmList(tab=self.tabmI6)
        self.linemI6 = self.plotmA.plot(
            self.time,
            self.tabmI6,
            name="I6",
            pen=pen,
            symbol="s",
            symbolSize=0.2,
            symbolBrush="g",
        )        
        
        pen = pg.mkPen(color=(250, 39, 237))
        self.tabmIPS = []
        self.clearTabmList(tab=self.tabmIPS)
        self.linemIPS = self.plotmA.plot(
            self.time,
            self.tabmIPS,
            name="IPS",
            pen=pen,
            symbol="o",
            symbolSize=1,
            symbolBrush="g",
        )
      
        mainLayout.addWidget(self.plotmV,1,0,1,6)
        mainLayout.addWidget(self.plotmA,2,0,1,6)
        self.linemI6.clear()
       
        mainLayout.setRowStretch(0,5)
        mainLayout.setColumnStretch(4, 4)
        self.P2PiloteGroupBox.setLayout(mainLayout)      
        
    def clearTabmList (self, tab = []):
        for i in range(self.plotRange):
            i = i
            tab.append(0)

if __name__ == "__main__":
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    app.shutdown()
    app = QtWidgets.QApplication([])

    # --- THIS IS WHERE app.setStyle("Fusion") SHOULD GO ---
    app.setStyle("Fusion") # Set the style once, right after QApplication creation
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText,QtGui.QColor(0, 0, 0))
    app.setPalette(palette)   
    widget = MYPLOT()
    
    widget.resize(2000, 1000)
    widget.show()

    sys.exit(app.exec())
    
