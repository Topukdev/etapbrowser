from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json

class Start(QMessageBox):
    def __init__(self):
        super().__init__()

        with open("./data/about.json", "r") as f:
            data = json.load(f)

        ad = data["name"]
        version = data["version"]
        lisans = data["license"]
        gelistirici = data["developer"]
        tip = data["type"]

        f.close()

        self.setWindowTitle("ETAP Tarayıcı Hakkında")
        self.setText(f"""
        {ad}
    
        Versiyon: {version}
    
        "Misyonumuz, Türkiye Yüzyılı'nda ülkemizi 
        yazılımsal açıdan bağımsız kılmaktır"
    
        Bu "{tip}", lisansı, kaynak kodu ve felsefesi
        doğrultusunda tümüyle bir özgür yazılımdır.
        "{ad}" adı Marginal Yazılım
        Limited Şirketi'ne ait olup, kaynak kodları
        kamuya açıktır.
    
        Geliştirici: {gelistirici}
        Lisans: {lisans}
    
        "Hedefimiz Kendi Tarayıcısı Olan Bir Türkiye!"
        """)
        self.setIcon(QMessageBox.Information)
