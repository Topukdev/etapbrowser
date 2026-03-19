import gi, os, json, sys
from classes import about, args as arghandler
from urllib.parse import quote_plus
from pathlib import Path
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")
from gi.repository import GLib, Gtk, Gdk ,Adw, WebKit, Gio

os.environ["WEBKIT_FORCE_SANDBOX"] = "0" 
os.environ["WPE_RENDERER"] = "1"

BASE_DIR = Path(__file__).resolve().parent #mutlak yol

class ETAPBrowser(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.topukdev.etapbrowser")
        GLib.set_application_name("ETA Ağ Tarayıcısı")

    def do_activate(self):
        ##args-----------------------
        self.parsed = arghandler.parse_args() #arg parsing
        
        ##WindowItself---------------
        window = Adw.ApplicationWindow(application=self)
        if self.parsed["size"]:
            window.set_default_size(self.parsed["size"][0], self.parsed["size"][1])
        else:
            window.set_default_size(1280, 768)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        window.set_content(main_box)

        ##Look-----------------------
        #önce css
        self.load_css()
        
        #headbar
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_hexpand(False)
        main_box.append(self.header_bar) 

        #urlbar
        self.urlbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.urlbar_box.set_hexpand(True)
        self.urlbar_box.set_margin_start(55)
        self.urlbar_box.set_margin_end(55)

        self.issecure = Gtk.Image.new_from_icon_name("channel-insecure-symbolic")
        self.issecure.add_css_class("secureicon")
        self.issecure.set_margin_end(5)
        self.issecure.set_tooltip_text("Bağlantı güvensiz")

        self.urlbar = Gtk.Entry()
        self.urlbar.set_placeholder_text("URL girin veya bir sözcük aratın...")
        self.urlbar.set_hexpand(True)
        self.urlbar.set_margin_start(0)
        self.urlbar.set_margin_end(0)
        self.urlbar.connect("activate", self.on_url)

        self.urlbar_box.append(self.issecure)
        self.urlbar_box.append(self.urlbar)

        #headbarbtns
        self.btn_back = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        self.btn_back.set_tooltip_text("Geri")
        self.btn_back.connect("clicked", lambda _: self.webview.go_back())
        self.btn_back.set_sensitive(False)

        self.btn_forward = Gtk.Button.new_from_icon_name("go-next-symbolic")
        self.btn_forward.set_tooltip_text("İleri")
        self.btn_forward.connect("clicked", lambda _: self.webview.go_forward())
        self.btn_forward.set_sensitive(False)

        self.btn_refresh = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        self.btn_refresh.set_tooltip_text("Yenile")
        self.btn_refresh.connect("clicked", lambda _: self.on_refresh_clicked())

        self.btn_home = Gtk.Button.new_from_icon_name("go-home-symbolic")
        self.btn_home.set_tooltip_text("EBA Anasayfa'ya Dön")

        self.btn_menu = Gtk.MenuButton()
        self.btn_menu.set_icon_name("open-menu-symbolic")

        #menu
        self.menu = Gio.Menu()
        self.menu.append("Hakkında", "app.about")
        
        self.popover = Gtk.PopoverMenu.new_from_model(self.menu)
        self.btn_menu.set_popover(self.popover)

        #progressbar
        self.load_bar = Gtk.ProgressBar()
        self.load_bar.set_visible(False) #başlangıçta gizli
        self.load_bar.add_css_class("osd") 

        #dizilim
        self.header_bar.pack_start(self.btn_back)
        self.header_bar.pack_start(self.btn_forward)
        self.header_bar.pack_start(self.btn_refresh)
        self.header_bar.pack_start(self.btn_home)    
        self.header_bar.set_title_widget(self.urlbar_box)
        self.header_bar.pack_end(self.btn_menu)

        ##WebKitView---------------------
        #webview
        self.webview = WebKit.WebView()
        self.webview.set_vexpand(True) #dikeyde tüm alanı kapla
        self.webview.set_hexpand(True) #yatayda bütün alanı kapla 
        
        if self.parsed["url"]: #url argümanı verilmişse
            self.webview.load_uri(arghandler.resolve_url(self.parsed["url"], BASE_DIR)) #parsed argümanı yükle
        else: #verilmemişse
            self.webview.load_uri("https://www.eba.gov.tr") #standart açılış

        #webviewfuncs
        self.webview.connect("load-changed", self.on_load_changed)
        self.webview.connect("load-failed-with-tls-errors", self.on_tls_error) #tls hata yönetimi
        self.webview.connect("enter-fullscreen", self.on_webkit_enter_fullscreen) #tam ekrana gir
        self.webview.connect("leave-fullscreen", self.on_webkit_leave_fullscreen) # tam ekrandan çık
        self.webview.connect("notify::estimated-load-progress", self.on_progress)
        self.webview.connect("notify::uri", self.update_url_bar) #her sayfa değiştiğinde urlbar'ı güncelle
        self.webview.connect("notify::is-loading", self.on_loading_changed)

        ##BrowserCore---------------------
        #webenginesettings
        settings = self.webview.get_settings()
        settings.set_enable_developer_extras(True)

        with open(f"{BASE_DIR}/data/data.json") as f:
            data = json.load(f)

        settings.set_user_agent(data["userAgent"])
        print(data["userAgent"]) #erişebildiğimizden emin olalım 
        
        settings.set_enable_webgl(True)  
        settings.set_hardware_acceleration_policy(WebKit.HardwareAccelerationPolicy.ALWAYS)
        settings.set_enable_media_stream(True)
        settings.set_enable_mediasource(True) 
        settings.set_allow_file_access_from_file_urls(True)
        settings.set_allow_universal_access_from_file_urls(True)

        #devtools?
        if self.parsed["devtools"] is not None: #eğer verilmişse
            settings.set_enable_developer_extras(self.parsed["devtools"]) #uygula
            if self.parsed["devtools"]: 
                self.webview.get_inspector().show()
        else:
            settings.set_enable_developer_extras(True)

        #actions
        aboutaction = Gio.SimpleAction.new("about", None)
        aboutaction.connect("activate", self.on_about)
        self.add_action(aboutaction)         

        #anadizilim
        main_box.append(self.load_bar)
        main_box.append(self.webview)
        
        window.present()

    def load_css(self):
        css_provider = Gtk.CssProvider() #css provider
        css_path = os.path.join(f"{BASE_DIR}/css/style.css") #./css/style/css

        try:
            css_provider.load_from_path(css_path) #dene
        except Exception as e:
            print(f"CSS yüklenemedi: {e}") #error handling
            return

        #tüm pencerelere uygula
        screen = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            screen,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION  # öncelik: 600
        )

    def on_refresh_clicked(self): #yenile butonu tıklandığında
        if self.webview.is_loading(): #mevcut yükleme varsa
            self.webview.stop_loading() #onu durdur
        else: #eğer boşsa
            self.webview.reload() #yenilemeyi başlat

    def on_url(self, entry): #urlparsing
        url = entry.get_text().strip()
        if not url:
            return
        
        if url.lower().endswith(".pdf"): #eğer pdf ise
            viewer_path = f"file://{BASE_DIR}/pdfjs/web/viewer.html" #görüntüleyici dizini
            
            # file:// ekle
            if not url.startswith(("http", "file")):
                url = f"file://{os.path.abspath(url)}"
                
            url = f"{viewer_path}?file={url}"
            self.webview.load_uri(url)
            return
            
        if url.startswith(("http://", "https://", "file:///")):
            pass
        elif url.startswith("/"): 
            url = "file://" + url
        elif "." not in url or " " in url:
            url = f"https://www.google.com/search?q={quote_plus(url)}" #eğer url değilse google'a yönlendir
        else:
            url = "https://" + url
            
        self.webview.load_uri(url) #yükle

    def on_progress(self, webview, param): #progressbar
        self.load_bar.set_visible(True)
        deger = webview.get_estimated_load_progress()
        self.load_bar.set_fraction(deger)

    def on_load_changed(self, webview, event): #back-forward yönetimi
        if event == WebKit.LoadEvent.STARTED: #yükleme başladığında
            self.btn_refresh.set_icon_name("window-close-symbolic") #ikon
            self.btn_refresh.set_tooltip_text("Durdur") #tooltip
        
        if event == WebKit.LoadEvent.FINISHED: #yüklenme tamamlandığında
            can_back = webview.can_go_back() #geri gidilebiliyor mu?
            self.btn_back.set_sensitive(can_back)
            
            can_forward = webview.can_go_forward() #ileri gidilebiliyor mu?
            self.btn_forward.set_sensitive(can_forward)

            self.btn_refresh.set_icon_name("view-refresh-symbolic") #ikon
            self.btn_refresh.set_tooltip_text("Yenile") #tooltip

            self.load_bar.set_visible(False)

    def on_loading_changed(self, webview, param): #sayfa yüklendiğinde
        if not webview.get_uri(): #url yoksa
            return #bir şey yapma
        self.update_security_icon(webview.get_uri()) #url varsa ikonu güncelle

    def update_security_icon(self, uri): #ikonu güncelle
        if uri.startswith("https://"): #eğer https ise
            self.issecure.set_from_icon_name("channel-secure-symbolic") #kilitli 
            self.issecure.set_tooltip_text("Bağlantı güvenli (HTTPS)") #tooltip
        elif uri.startswith("http://"): #http ise
            self.issecure.set_from_icon_name("channel-insecure-symbolic") #kilitsiz
            self.issecure.set_tooltip_text("Bağlantı güvensiz (HTTP)") #tooltip
        elif uri.startswith("file://"): #dosya ise (file://)
            self.issecure.set_from_icon_name("folder-symbolic") #dosya klasörü ikonu
            self.issecure.set_tooltip_text("Yerel dosya") #tooltip
        else:
            #bilinmeyen protokol
            self.issecure.set_from_icon_name("dialog-question-symbolic") #bilinmeyen
            self.issecure.set_tooltip_text("Bilinmeyen protokol") #tooltip

    def update_url_bar(self, webview, event): 
        uri = webview.get_uri() #hedef url'yi al
        if uri:
            if uri.startswith("https://www.eba.gov.tr/"): #eğer hedef eba ise bir şey yapma
                self.urlbar.set_text("")
            else:
                self.urlbar.set_text(uri) #urlbar'daki url'yi güncelle        
    
    def on_tls_error(self, webview, failing_uri, certificate, errors): #tls hata yönetimi
        return True #şimdilik atlayalım
    
    def on_webkit_enter_fullscreen(self, webview): #tam ekran desteği
        self.header_bar.set_visible(False)
        
        return False 

    def on_webkit_leave_fullscreen(self, webview): 
        self.header_bar.set_visible(True)
        
        return False
    
    def on_about(self, action, param):
        #Hakkında
        about.show_about(self.get_active_window(), BASE_DIR)

app = ETAPBrowser()
app.run([sys.argv[0]])