import os
import subprocess
import threading
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

class ControlPanel(Gtk.Window):
    def __init__(self):
        super().__init__(title="Control Panel")
        
        # Detect the display server
        display_server = os.getenv('XDG_SESSION_TYPE', 'X11')
        print(f"Detected display server: {display_server}")

        # Set the window title with the user's name
        user_name = os.getenv("USER") or os.getenv("USERNAME")  # Get the system user name
        self.set_title(f"Hello, {user_name}!")

        # Configure the window with a standard GTK bar
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        # If we are on Wayland, enable window borders
        if display_server == 'Wayland':
            self.set_decorated(True)  # This adds window borders

        # Look for the icon in the root folder
        current_dir = os.getcwd()  # Get the current directory
        icon_path = os.path.join(current_dir, "/usr/share/cuerd_settings/icons/settings.svg")  # Adjust the filename as necessary

        # If the file is found, set the icon for the window and the taskbar
        if os.path.exists(icon_path):
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            self.set_icon(icon_pixbuf)  # Set the icon for the window
            self.set_default_icon_from_file(icon_path)  # Set the icon for the taskbar

        # Menu bar
        menu_bar = Gtk.MenuBar()

        # "Help" menu
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)

        about_item = Gtk.MenuItem(label="About...")
        about_item.connect("activate", self.show_about_dialog)
        help_menu.append(about_item)

        menu_bar.append(help_item)

        # Main container with scrolling
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)  # Disable horizontal scrolling

        # Create a vertical container for the sections
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_vexpand(True)
        main_box.set_hexpand(True)

        # Section: System and Security
        self.create_section(main_box, "System and Security", "System security and configuration", "security-low.svg", [
            ("Firewall", "firewall-config", "fire.svg"),
            ("Repository Configuration", "sakura -e pkexec setup-repos", "administration.svg"),
            ("Clean System", "bleachbit", "edit-clear-all.svg"),
            ("App Store", "bauh", "pirut.svg"),
            ("Login Window", "pkexec lightdm-settings", "launch.svg")
        ])

        # Section: Internet and Wireless
        self.create_section(main_box, "Connections", "Network and wireless device configuration", "conn.svg", [
            ("Network Connections", "nm-connection-editor", "network-wired.svg"),
            ("Bluetooth Adapters", "blueman-adapters", "adp_b.svg"),
            ("Bluetooth Devices", "blueman-manager", "bluetooth.svg"),
        ])
        
        # Section: Energy
        self.create_section(main_box, "Energy", "Power management options and screensaver preferences", "energy.svg", [
            ("Power Management", "xfce4-power-manager-settings", "xfce4-battery-plugin.svg"),
            ("Screensaver", "xfce4-screensaver-preferences", "screensaver.svg"),
        ])
        
        # Section: Hardware and Sound
        self.create_section(main_box, "Hardware", "Hardware and sound device configuration", "hardware.svg", [
            ("Printer Service Configuration", "sakura -e pkexec cups-switch", "printer.svg"),
            ("NVIDIA Driver Installer", "sakura -e pkexec nvidia_installer", "nvidia.svg"),
            ("Audio", "pavucontrol", "audio-volume-high.svg"),
            ("Equalizer (Pipewire)", "jamesdsp", "equalizer.svg"),
            ("Display (X11/Xorg)", "arandr", "x11.svg"),
            ("Display (Wayland)", "wdisplays", "way.svg"),
            ("Storage", "gnome-disks", "disk-utility.svg"),
            ("Hardware Information", "hardinfo", "hwinfo.svg")
        ])

        # Section: Users and Groups
        self.create_section(main_box, "Accessibility", "Accessibility options and user configuration", "accs.svg", [
            ("Manage Users or Groups", "users-admin", "user.svg"),
            ("Default Programs", os.path.join(os.getcwd(), "tools", "mime"), "application-x-m4.svg"),
            ("Keyboard", "ibus", "keys.svg"),
            ("Time/Date Management", "time-admin", "clock.svg"),
            ("Calendar", "orage", "calendar.svg"),
        ])

        # Section: Customization
        self.create_section(main_box, "Customization", "Options to customize the system appearance", "preferences-desktop-theme.svg", [
            ("Conkyman", "/usr/share/conkyman/conkyman.py", "conkyman.svg"),
            ("Wallpaper", "nitrogen", "image.svg"),
            ("Text Fonts", "font-manager", "fonts.svg"),
            ("Customize Qt Appearance", "qt5ct", "qt.svg"),
            ("Customize GTK Appearance", "nwg-look", "preferences-desktop-theme-global.svg"),
        ])
            
        # Section: Advanced
        self.create_section(main_box, "Configuration Files", "Quick access to configuration files", "text-editor.svg", [
            ("Sway Config File", "xdg-open ~/.config/sway/config", "sway.svg"),
            ("i3 Config File", "xdg-open ~/.config/i3/config", "i3.svg"),
            ("Awesome Config File", "xdg-open ~/.config/awesome/rc.lua", "awesome.svg")
        ])

        # Add the main container to the scrolling container
        scrolled_window.add(main_box)

        # Add the main container to the window
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        window_box.pack_start(menu_bar, False, False, 0)
        window_box.pack_start(scrolled_window, True, True, 0)

        # Add the container to the window
        self.add(window_box)

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
        icon_path = os.path.join(os.getcwd(), "/usr/share/cuerd_settings/ico", section_icon)
        icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 24, 24))
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

        # Create a grid for the buttons
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_hexpand(True)
        grid.set_vexpand(True)

        # Calculate the grid size
        num_buttons = len(buttons)
        grid_size = int(num_buttons**0.5)  # Calculate the size of the nearest square side
        if grid_size**2 < num_buttons:
            grid_size += 1

        # Add buttons to the grid
        for i, (label, command, icon_name) in enumerate(buttons):
            button = Gtk.Button(label=label)
            
            # Set the icon with size 18x18
            icon_path = os.path.join(os.getcwd(), "/usr/share/cuerd_settings/ico", icon_name)
            icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 18, 18))
            button.set_image(icon)
            button.set_always_show_image(True)
            
            # Set hexpand and vexpand for buttons
            button.set_hexpand(True)
            button.set_vexpand(True)
            button.set_size_request(100, 40)  # Increase button height
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
        about_dialog.set_version("1.0 v090125b Elena")
        about_dialog.set_comments("Exclusive control panel for CuerdOS GNU/Linux.")
        about_dialog.set_website("https://github.com/CuerdOS")
        about_dialog.set_website_label("GitHub")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)

        # Logo path
        current_dir = os.getcwd()
        logo_path = os.path.join(current_dir, "/usr/share/cuerd_settings/icons/settings_about.svg")

        about_dialog.set_authors([
            "Ale D.M ",
            "Leo H. Pérez (GatoVerde95)",
            "Pablo G.",
            "Welkis",
            "GatoVerde95 Studios",
            "CuerdOS Community",
            "Org. CuerdOS",
            "Stage 49"
        ])
        about_dialog.set_copyright("© 2025 CuerdOS")

        if os.path.exists(logo_path):
            logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file(logo_path)
            logo_pixbuf = logo_pixbuf.scale_simple(150, 150, GdkPixbuf.InterpType.BILINEAR)
            about_dialog.set_logo(logo_pixbuf)

        about_dialog.run()
        about_dialog.destroy()

def main():
    win = ControlPanel()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
