import os
import subprocess
import threading
import gi
import json
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

class ControlPanel(Gtk.Window):
    def __init__(self):
        super().__init__(title="CuerdOS Settings")

        # Detect the display server
        display_server = os.getenv('XDG_SESSION_TYPE', 'X11')
        print(f"Detected display server: {display_server}")

        # Set the window title with the user's name
        user_name = os.getenv("USER") or os.getenv("USERNAME")  # Get the system user's name
        self.set_title(f"Hello, {user_name}!")

        # Configure the window with standard GTK title bar
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        # If on Wayland, enable window borders
        if display_server == 'Wayland':
            self.set_decorated(True)  # This adds window borders

        # Search for the icon in the root folder
        current_dir = os.getcwd()  # Get the current directory
        icon_path = self.find_icon_path(current_dir, "/usr/share/cuerd_settings/icons/settings")

        # If the file is found, set the icon for the window and taskbar
        if icon_path:
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            self.set_icon(icon_pixbuf)  # Set the icon for the window
            self.set_default_icon_from_file(icon_path)  # Set the icon for the taskbar

        # Menu bar
        menu_bar = Gtk.MenuBar()

        # "Help" menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="Help")
        file_item.set_submenu(file_menu)

        about_item = Gtk.MenuItem(label="About...")
        about_item.connect("activate", self.show_about_dialog)
        file_menu.append(about_item)

        # "Settings" menu
        settings_menu = Gtk.Menu()
        settings_item = Gtk.MenuItem(label="Settings")
        settings_item.set_submenu(settings_menu)

        icon_pack_item = Gtk.MenuItem(label="Choose Icon Pack")
        icon_pack_item.connect("activate", self.show_icon_pack_dialog)
        settings_menu.append(icon_pack_item)

        menu_bar.append(file_item)
        menu_bar.append(settings_item)

        # Main container with scroll bar
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)  # Disable horizontal scrolling

        # Create a vertical container for the sections
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_vexpand(True)
        main_box.set_hexpand(True)

        # Load icon pack configuration
        self.load_icon_pack_config()

        # Section: System and Security
        self.create_section(main_box, "System and Security", "System security and configuration", "security-low", [
            ("Firewall", "firewall-config", "fire"),
            ("Repository Configuration", "sakura -e pkexec setup-repos", "administration"),
            ("Clean System", "bleachbit", "edit-clear-all"),
            ("App Store", "bauh", "pirut"),
            ("Login Window", "pkexec lightdm-settings", "launch")
        ])

        # Section: Internet and Wireless
        self.create_section(main_box, "Connections", "Network and wireless device configuration", "conn", [
            ("Network Connections", "nm-connection-editor", "network-wired"),
            ("Bluetooth Adapters", "blueman-adapters", "adp_b"),
            ("Bluetooth Devices", "blueman-manager", "bluetooth"),
        ])
        
        # Section: Energy
        self.create_section(main_box, "Energy", "Power management and screensaver preferences", "energy", [
            ("Power Management", "xfce4-power-manager-settings", "xfce4-battery-plugin"),
            ("Screensaver", "xfce4-screensaver-preferences", "screensaver"),
        ])
        
        # Section: Hardware and Sound
        self.create_section(main_box, "Hardware", "Hardware and sound device configuration", "hardware", [
            ("Printer Service Configuration", "sakura -e pkexec cups-switch", "printer"),
            ("NVIDIA Driver Installer", "sakura -e pkexec nvidia_installer", "nvidia"),
            ("Audio", "pavucontrol", "audio-volume-high"),
            ("Equalizer (Pipewire)", "jamesdsp", "equalizer"),
            ("Display (X11/Xorg)", "arandr", "x11"),
            ("Display (Wayland)", "wdisplays", "way"),
            ("Storage", "gnome-disks", "disk-utility"),
            ("Hardware Information", "hardinfo", "hwinfo")
        ])

        # Section: Users and Groups
        self.create_section(main_box, "Accessibility", "Accessibility options and user configuration", "accs", [
            ("Manage Users or Groups", "users-admin", "user"),
            ("Default Programs", os.path.join(os.getcwd(), "tools", "mime"), "application-x-m4"),
            ("Keyboard", "ibus", "keys"),
            ("Time/Date Management", "time-admin", "clock"),
            ("Calendar", "orage", "calendar"),
        ])

        # Section: Customization
        self.create_section(main_box, "Customization", "Options to customize system appearance", "preferences-desktop-theme", [
            ("Conkyman", "/usr/share/conkyman/conkyman.py", "conkyman"),
            ("Wallpaper", "nitrogen", "image"),
            ("Text Fonts", "font-manager", "fonts"),
            ("Customize Qt Appearance", "qt5ct", "qt"),
            ("Customize GTK Appearance", "nwg-look", "preferences-desktop-theme-global"),
        ])
            
        # Section: Advanced
        self.create_section(main_box, "Configuration Files", "Quick access to configuration files", "text-editor", [
            ("Sway Config File", "xdg-open ~/.config/sway/config", "sway"),
            ("i3 Config File", "xdg-open ~/.config/i3/config", "i3"),
            ("AwesomeWM Config File", "xdg-open ~/.config/awesome/rc.lua", "awesome")
        ])

        # Add the main container to the scrollable container
        scrolled_window.add(main_box)

        # Add the main container to the window
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        window_box.pack_start(menu_bar, False, False, 0)
        window_box.pack_start(scrolled_window, True, True, 0)

        # Add the container to the window
        self.add(window_box)

    def find_icon_path(self, base_dir, icon_name):
        """Search for the icon file with .svg or .png extension"""
        for ext in [".svg", ".png"]:
            path = os.path.join(base_dir, icon_name + ext)
            if os.path.exists(path):
                return path
        return None

    def create_section(self, parent_box, title, description, section_icon, buttons):
        # Create a container for the section
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        section_box.set_margin_start(20)
        section_box.set_margin_end(20)
        section_box.set_margin_top(5)
        section_box.set_margin_bottom(10)
        section_box.set_hexpand(True)
        section_box.set_vexpand(True)

        # Create a horizontal container for the title and icon
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        icon_path = self.find_icon_path(f"/usr/share/cuerd_settings/ico/{self.icon_pack}", section_icon)
        
        # Verify the existence of the file before loading it
        if icon_path:
            icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 24, 24))
        else:
            print(f"Icon file not found: {icon_path}")
            icon = Gtk.Image()  # Create an empty Gtk.Image object if the file is not found
        
        title_box.pack_start(icon, False, False, 0)

        # Create a title for the section
        section_label = Gtk.Label(label=f"<b>{title}</b>")
        section_label.set_justify(Gtk.Justification.LEFT)
        section_label.set_use_markup(True)
        section_label.set_halign(Gtk.Align.START)
        title_box.pack_start(section_label, False, False, 0)

        # Add the title container to the section
        section_box.pack_start(title_box, False, False, 0)

        # Create a label for the description
        description_label = Gtk.Label(label=description)
        description_label.set_justify(Gtk.Justification.LEFT)
        description_label.set_halign(Gtk.Align.START)
        section_box.pack_start(description_label, False, False, 0)

        # Create a Grid for the buttons
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_hexpand(True)
        grid.set_vexpand(True)

        # Calculate the grid size
        num_buttons = len(buttons)
        grid_size = int(num_buttons**0.5)  # Calculate the closest square size
        if grid_size**2 < num_buttons:
            grid_size += 1

        # Add buttons to the Grid
        for i, (label, command, icon_name) in enumerate(buttons):
            button = Gtk.Button(label=label)
            
            # Configure the icon with size 18x18
            icon_path = self.find_icon_path(f"/usr/share/cuerd_settings/ico/{self.icon_pack}", icon_name)
            if icon_path:
                icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 18, 18))
            else:
                print(f"Icon file not found: {icon_path}")
                icon = Gtk.Image()  # Create an empty Gtk.Image object if the file is not found
            
            button.set_image(icon)
            button.set_always_show_image(True)
            
            # Set hexpand and vexpand for the buttons
            button.set_hexpand(True)
            button.set_vexpand(True)
            button.set_size_request(100, 40)  # Increase the height of the buttons
            button.connect("clicked", self.on_button_clicked, command)
            grid.attach(button, i % grid_size, i // grid_size, 1, 1)

        section_box.pack_start(grid, True, True, 0)
        parent_box.pack_start(section_box, False, False, 0)

    def on_button_clicked(self, widget, command):  # pylint: disable=unused-argument
        # Create a thread to run the command in the background
        threading.Thread(target=self.run_command, args=(command,)).start()

    def run_command(self, command):
        # Run the command in a separate thread
        try:
            if command.startswith("xdg-open"):
                subprocess.run(command, shell=True, check=True)
            else:
                subprocess.run(command, shell=True, check=True)
            print(f"Command executed: {command}")
        except subprocess.CalledProcessError as e:
            # If the command is qt5ct, do not show the error message
            if 'qt5ct' in command:
                print(f"Error executing command {command}: {e}")
            else:
                print(f"Error executing command {command}: {e}")
                self.show_error_dialog(f"The command could not be executed: {command}")
        except FileNotFoundError:
            print(f"Command not found: {command}")
            self.show_error_dialog(f"The program was not found: {command}")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.show_error_dialog(f"An error occurred: {e}")

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.format_secondary_text(
            "Please check that the program is installed and accessible."
        )
        dialog.run()
        dialog.destroy()

    def show_about_dialog(self, widget):  # pylint: disable=unused-argument
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("CuerdOS Settings")
        about_dialog.set_version("1.0 v300125a Elena")
        about_dialog.set_comments("Control panel exclusively for CuerdOS GNU/Linux.")
        about_dialog.set_website("https://github.com/CuerdOS")
        about_dialog.set_website_label("GitHub")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        
        about_dialog.set_authors([
            "Ale D.M ",
            "Leo H. Pérez (GatoVerde95)",
            "Pablo G.",
            "Welkis",
            "GatoVerde95 Studios",
            "CuerdOS Community"
        ])
        about_dialog.set_copyright("© 2025 CuerdOS")

        # Logo path
        current_dir = os.getcwd()
        logo_path = self.find_icon_path(current_dir, "/usr/share/cuerd_settings/icons/settings_about")

        if logo_path:
            logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file(logo_path)
            logo_pixbuf = logo_pixbuf.scale_simple(150, 150, GdkPixbuf.InterpType.BILINEAR)
            about_dialog.set_logo(logo_pixbuf)

        about_dialog.run()
        about_dialog.destroy()

    def show_icon_pack_dialog(self, widget):  # pylint: disable=unused-argument
        dialog = Gtk.Dialog(title="Choose Icon Pack", transient_for=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        box = dialog.get_content_area()
        label = Gtk.Label(label="Select an icon pack:")
        box.add(label)

        icon_pack_store = Gtk.ListStore(str)
        
        # Detect icon pack folders and .png or .svg files
        icon_packs = []
        icon_dirs = ["/usr/share/cuerd_settings/ico/Qogir", "/usr/share/cuerd_settings/ico/CuerdOS-Elementary"]
        for icon_dir in icon_dirs:
            if os.path.exists(icon_dir):
                if any(fname.endswith(('.png', '.svg')) for fname in os.listdir(icon_dir)):
                    icon_packs.append(os.path.basename(icon_dir))
        
        for pack in icon_packs:
            icon_pack_store.append([pack])
        
        combo = Gtk.ComboBox.new_with_model(icon_pack_store)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 0)
        
        # Select "CuerdOS-Elementary" by default
        default_index = icon_packs.index("CuerdOS-Elementary") if "CuerdOS-Elementary" in icon_packs else 0
        combo.set_active(default_index)
        box.add(combo)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            model = combo.get_model()
            index = combo.get_active()
            selected_pack = model[index][0]
            self.save_icon_pack_config(selected_pack)

        dialog.destroy()

    def save_icon_pack_config(self, icon_pack):
        config_path = os.path.join(os.getcwd(), "icon_pack_config.json")
        with open(config_path, 'w') as config_file:
            json.dump({"icon_pack": icon_pack}, config_file)
        print(f"Icon pack configuration saved: {icon_pack}")

    def load_icon_pack_config(self):
        config_path = os.path.join(os.getcwd(), "icon_pack_config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                self.icon_pack = config.get("icon_pack", "CuerdOS-Elementary")
                print(f"Icon pack configuration loaded: {self.icon_pack}")
        else:
            self.icon_pack = "CuerdOS-Elementary"
            print("No icon pack configuration found. Using 'CuerdOS-Elementary' by default.")

def main():
    win = ControlPanel()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()