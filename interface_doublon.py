import os
import sys
import geopandas as gpd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QProgressBar, QComboBox, QListWidget

class DoublonDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Détection de doublons par RefPM')
        self.setGeometry(100, 100, 500, 250)

        self.label_src_dir = QLabel('Dossier Source:')
        self.line_edit_src_dir = QLineEdit()
        self.button_browse_src = QPushButton('Parcourir')
        self.button_browse_src.clicked.connect(self.browse_src_directory)

        self.label_dst_dir = QLabel('Dossier Destination:')
        self.line_edit_dst_dir = QLineEdit()
        self.button_browse_dst = QPushButton('Parcourir')
        self.button_browse_dst.clicked.connect(self.browse_dst_directory)

        self.progress_bar = QProgressBar()

        self.label_column = QLabel('Colonnes pour vérifier les doublons:')
        self.list_widget_columns = QListWidget()
        self.list_widget_columns.setSelectionMode(QListWidget.MultiSelection)

        self.button_process = QPushButton('Lancer le traitement')
        self.button_process.clicked.connect(self.process_data)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_src_dir)
        hbox_src = QHBoxLayout()
        hbox_src.addWidget(self.line_edit_src_dir)
        hbox_src.addWidget(self.button_browse_src)
        vbox.addLayout(hbox_src)

        vbox.addWidget(self.label_dst_dir)
        hbox_dst = QHBoxLayout()
        hbox_dst.addWidget(self.line_edit_dst_dir)
        hbox_dst.addWidget(self.button_browse_dst)
        vbox.addLayout(hbox_dst)

        vbox.addWidget(self.label_column)
        vbox.addWidget(self.list_widget_columns)

        vbox.addWidget(self.progress_bar)
        vbox.addWidget(self.button_process)

        self.setLayout(vbox)

        self.setStyleSheet('''
            QWidget {
                background-color: #f0f0f0;
                color: #282c34;
                font-size: 14px;
            }
            QLabel {
                padding: 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: #f0f0f0;
                border: none;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                background-color: #f0f0f0;
                color: #282c34;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #f0f0f0;
                background-color: #f0f0f0;
                color: #282c34;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        ''')

    def browse_src_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        src_dir = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier source", options=options)
        self.line_edit_src_dir.setText(src_dir)
        self.load_shapefile_columns()

    def browse_dst_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dst_dir = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de destination", options=options)
        self.line_edit_dst_dir.setText(dst_dir)

    def load_shapefile_columns(self):
        src_dir = self.line_edit_src_dir.text()
        if not os.path.exists(src_dir):
            return

        shapefile_list = [file for file in os.listdir(src_dir) if file.endswith('.shp')]
        if not shapefile_list:
            return

        shapefile_path = os.path.join(src_dir, shapefile_list[0])
        gdf = gpd.read_file(shapefile_path)

        self.list_widget_columns.clear()
        self.list_widget_columns.addItems(gdf.columns)

    def process_data(self):
        src_dir = self.line_edit_src_dir.text()
        dst_dir = self.line_edit_dst_dir.text()

        if not os.path.exists(src_dir):
            print("Le dossier source n'existe pas.")
            return

        shapefile_list = [file for file in os.listdir(src_dir) if file.endswith('.shp')]
        if not shapefile_list:
            print("Aucun fichier shape n'a été trouvé dans le dossier source.")
            return

        shapefile_path = os.path.join(src_dir, shapefile_list[0])
        gdf = gpd.read_file(shapefile_path)

        if "RefPM" not in gdf.columns:
            print("Le fichier shape ne contient pas de colonne 'RefPM'.")
            return

        selected_columns = [item.text() for item in self.list_widget_columns.selectedItems()]
        if not selected_columns:
            print("Aucune colonne sélectionnée pour vérifier les doublons.")
            return

        duplicates = gdf[gdf.duplicated(subset=selected_columns, keep=False)]

        self.progress_bar.setValue(50)

        if dst_dir:
            duplicates_shapefile_path = os.path.join(dst_dir, "duplicates.shp")
            duplicates.to_file(duplicates_shapefile_path)

            self.progress_bar.setValue(100)
            print("Les doublons ont été enregistrés dans un nouveau fichier shape dans le dossier destination.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DoublonDetectionApp()
    window.show()
    sys.exit(app.exec_())
