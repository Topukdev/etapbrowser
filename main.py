from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import * 
import sys, os, urllib.parse, json, classes.settings, classes.sight, classes.theme

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-background-networking"

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        #Pencere
        self.setWindowTitle("ETAP Tarayıcı")
        self.resize(800, 600)
        self.wid = QWidget()
        self.lay = QVBoxLayout()
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.wid)
        self.wid.setLayout(self.lay)
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        with open("./data/data.json", "r") as f:
            self.data = json.load(f)

        #BrowserCore
        self.webengine = QWebEngineView()
        self.webengine.setUrl(QUrl("https://www.duckduckgo.com"))
        self.webengine.urlChanged.connect(self.updateUrlBar)
        self.webengine.urlChanged.connect(self.checkUrl)
        self.webengine.page().profile().downloadRequested.connect(self.on_download_requested)

        self.progressbar = QProgressBar()
        self.progressbar.setTextVisible(False)
        self.progressbar.hide()

        self.downloadbar = QProgressBar()
        self.downloadbar.setTextVisible(False)
        self.downloadbar.hide()
        
        profile = QWebEngineProfile.defaultProfile()
        #profile.setPersistentStoragePath("./profile/0")
        #profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies) çok yakında!

        profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.webengine.loadStarted.connect(lambda: self.progressbar.show())
        self.webengine.loadProgress.connect(self.progressbar.setValue)
        self.webengine.loadFinished.connect(lambda: self.progressbar.hide())
        
        #Arayüz
        self.spacer = QWidget()
        self.spacer.setFixedWidth(1)

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("ETAP URL...")
        self.urlbar.returnPressed.connect(lambda: self.navigateToUrl(self.urlbar.text()))

        self.backbutton = QAction(text="Geri")
        self.backbutton.triggered.connect(lambda: self.webengine.back())

        self.homebutton = QAction(text="Ev")
        self.homebutton.triggered.connect(lambda: self.webengine.setUrl(QUrl("https://www.duckduckgo.com")))

        self.forwardbutton = QAction(text="İleri")
        self.forwardbutton.triggered.connect(lambda: self.webengine.forward())

        self.searchbar = QLineEdit()
        self.searchbar.setPlaceholderText("ETAP Arama...")
        self.searchbar.returnPressed.connect(self.performSearch)

        self.settinsButton = QAction(text="Ayarlar")
        self.settinsButton.triggered.connect(self.showSettings)

        self.spaceriki = QWidget()
        self.spaceriki.setFixedWidth(1)
        
        #Sıralama
        self.lay.addWidget(self.progressbar)
        self.lay.addWidget(self.downloadbar)
        self.lay.addWidget(self.webengine)
        self.toolbar.addWidget(self.spacer)
        self.toolbar.addAction(self.backbutton)
        self.toolbar.addAction(self.forwardbutton)
        self.toolbar.addWidget(self.urlbar)
        self.toolbar.addWidget(self.searchbar)
        self.toolbar.addAction(self.homebutton)
        self.toolbar.addAction(self.settinsButton)
        self.toolbar.addWidget(self.spaceriki)

    def on_download_requested(self, download):
        fileName = download.suggestedFileName()
        
        savePath, _ = QFileDialog.getSaveFileName(
            self,
            "Dosyayı Kaydet",
            os.path.join(os.path.expanduser("~"), "İndirilenler", fileName),
            "Tüm Dosyalar (*.*)"
        )
        
        if savePath:
            download.setPath(savePath)
            download.accept()

            self.downloadbar.show()
            self.downloadbar.setValue(0)
            
            download.finished.connect(lambda: self.download_finished(savePath))
            download.downloadProgress.connect(self.download_progress)

    def download_finished(self, path):
        """İndirme tamamlandığında"""
        self.downloadbar.hide()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("İndirme Tamamlandı")
        msg.setText(f"Dosya başarıyla indirildi:\n{path}")
        msg.exec_()

    def download_progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            progress = int((bytes_received / bytes_total)) * 100
            self.downloadbar.setValue(progress)
            print(f"İndirme: %{progress:.1f}")

            QApplication.processEvents()
    
    def showSettings(self):
        dialog = classes.settings.Settings(self)
        dialog.exec_()

    def performSearch(self):
        query = urllib.parse.quote(self.searchbar.text())
        self.webengine.setUrl(QUrl(f"https://duckduckgo.com/?q={query}"))

    def updateUrlBar(self):
        self.urlbar.setText(self.webengine.url().toString())
    
    def navigateToUrl(self, url):
        url = self.urlbar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self.webengine.setUrl(QUrl(url))

    def checkUrl(self, url):
        allowedPages = []

        if not self.data["kisitli_mod"]:
            return

        if self.data["kisitli_mod"] == True:
            allowedPages = [
                "eba.gov.tr",
                "meb.gov.tr",
                "mebi.eba.gov.tr",
                "duckduckgo.com",
                "google.com",
                "restricted.html" #Sitenin yasaklı olduğunu bildiren bir sayfa
            ]
        else:
            pass

        current_host = url.host().lower()

        if url.isLocalFile() and "restricted.html" in url.toString():
                    return

        allowed = False
        for domain in allowedPages:
            if current_host == domain or current_host.endswith("." + domain):
                allowed = True
                break
    
        if not allowed:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            restricted_path = os.path.join(current_dir, "html", "restricted.html")
            self.webengine.setUrl(QUrl.fromLocalFile(restricted_path))

if __name__ == "__main__":
    application = QApplication(sys.argv)
    
    win = Browser()
    win.show()

    with open("./data/data.json", "r") as f:
        data = json.load(f)

    koyumod = data["koyu?"]

    themer = classes.theme.ThemeManager()

    f.close()
    
    if koyumod == True:
        themer.load_theme("dark") 
    else:
        themer.load_theme("light") 
    
    themer.apply_to_app(application)

    msg = classes.sight.Start()
    msg.exec_()
    
    sys.exit(application.exec_())