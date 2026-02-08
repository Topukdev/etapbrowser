from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys, json

class Settings(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        
        #Pencere
        self.setWindowTitle("Ayarlar")
        self.resize(600, 400)
        self.lay = QVBoxLayout()
        self.lay.setContentsMargins(10, 10, 10, 10)
        self.lay.setSpacing(20)
        self.setLayout(self.lay)

        #Widgetlar

        self.lay2 = QHBoxLayout()
        self.lay2.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Öğretmen Gözetimi")
        label.setFont(QFont("Calibri", 14, QFont.Bold))

        text = QLabel("Kısıtlı Mod: ")
        self.checkbox = QCheckBox()
        self.checkbox.setToolTip("""Sadece EBA ve MEBİ gibi\neğitim materyallerine izin\nverir. (Tarayıcının yeniden\nbaşlatılmasını gerektirir)""")
        text.setToolTip("""Sadece EBA ve MEBİ gibi\neğitim materyallerine izin\nverir. (Tarayıcının yeniden\nbaşlatılmasını gerektirir)""")

        self.lay3 = QHBoxLayout()
        self.lay3.setContentsMargins(0, 0, 0, 0)

        label2 = QLabel("Görünüm")
        label2.setFont(QFont("Calibri", 14, QFont.Bold))

        tema = QLabel("Koyu Tema: ")
        self.themebox = QCheckBox()
        self.themebox.setToolTip("""Koyu temayı aktif eder. (Tarayıcının yeniden\nbaşlatılmasını gerektirir)""")
        tema.setToolTip("""Koyu temayı aktif eder. (Tarayıcının yeniden\nbaşlatılmasını gerektirir)""")

        with open("./data/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.checkbox.setChecked(data["kisitli_mod"])
            self.themebox.setChecked(data["koyu?"])

        self.checkbox.stateChanged.connect(self.whenCheckboxChanged)
        self.themebox.stateChanged.connect(self.whenThemeChanged)

        #Sıralama
        self.lay.addWidget(label)
        self.lay2.addWidget(text)
        self.lay2.addWidget(self.checkbox)
        self.lay2.addStretch()
        self.lay.addLayout(self.lay2)
        self.lay.addWidget(label2)
        self.lay.addLayout(self.lay3)
        self.lay3.addWidget(tema)
        self.lay3.addWidget(self.themebox)
        self.lay3.addStretch()
        self.lay.addStretch()

    def whenCheckboxChanged(self, state):
        # Dosyayı oku
        with open("./data/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Değeri güncelle (state: 2=Checked/True, 0=Unchecked/False)
        data["kisitli_mod"] = (state == 2)

        f.close()
        
        # Dosyaya yaz
        with open("./data/data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        f.close()

    def whenThemeChanged(self, state):
        # Dosyayı oku
        with open("./data/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Değeri güncelle (state: 2=Checked/True, 0=Unchecked/False)
        data["koyu?"] = (state == 2)

        f.close()
        
        # Dosyaya yaz
        with open("./data/data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        f.close()

if False:
    app = QApplication(sys.argv)
    win = Settings(None)
    win.show()
    app.exec_()