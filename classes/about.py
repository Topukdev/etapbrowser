import gi, json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

def show_about(parent_window, BASE_DIR):  # parent pencere
    with open(f"{BASE_DIR}/data/about.json") as f:
        info = json.load(f)

    dialog = Adw.AboutWindow()
    dialog.set_application_name(info["name"]) #isim
    dialog.set_version(info["version"])
    dialog.set_developer_name(info["developer"])
    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.set_transient_for(parent_window) 
    
    dialog.present()