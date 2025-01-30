import os
import subprocess
import threading
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

class ControlPanel(Gtk.Window):
    def __init__(self):
        super().__init__(title="Ajustes de CuerdOS")
        
        # Detectar el servidor gráfico
        display_server = os.getenv('XDG_SESSION_TYPE', 'X11')
        print(f"Servidor gráfico detectado: {display_server}")

        # Configurar el título de la ventana con el nombre del usuario
        user_name = os.getenv("USER") or os.getenv("USERNAME")  # Obtener el nombre del usuario del sistema
        self.set_title(f"¡Hola, {user_name}!")

        # Configurar la ventana con barra estándar de GTK
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Si estamos en Wayland, habilitar bordes en la ventana
        if display_server == 'Wayland':
            self.set_decorated(True)  # Esto agrega los bordes de la ventana

        # Buscar el icono en la carpeta raíz
        current_dir = os.getcwd()  # Obtener el directorio actual
        icon_path = os.path.join(current_dir, "/usr/share/cuerd_settings/icons/settings.svg")  # Ajusta el nombre del archivo según sea necesario

        # Si se encuentra el archivo, configuramos el icono para la ventana y para la barra de tareas
        if os.path.exists(icon_path):
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            self.set_icon(icon_pixbuf)  # Establece el icono para la ventana
            self.set_default_icon_from_file(icon_path)  # Establece el icono para la barra de tareas

        # Barra de menús
        menu_bar = Gtk.MenuBar()

        # Menú "Archivo"
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="Ayuda")
        file_item.set_submenu(file_menu)

        acerca_item = Gtk.MenuItem(label="Acerca de...")
        acerca_item.connect("activate", self.show_about_dialog)
        file_menu.append(acerca_item)

        menu_bar.append(file_item)

        # Contenedor principal con barra de desplazamiento
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)  # Deshabilitar desplazamiento horizontal

        # Crear un contenedor vertical para las secciones
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_vexpand(True)
        main_box.set_hexpand(True)

        # Sección: System and Security
        self.crear_seccion(main_box, "Sistema y Seguridad", "Seguridad del sistema y configuración", "security-low.svg", [
            ("Cortafuegos", "firewall-config", "fire.svg"),
            ("Configuracion de Repositorios", "sakura -e pkexec setup-repos", "administration.svg"),
            ("Limpiar el sistema", "bleachbit", "edit-clear-all.svg"),
            ("Tienda de aplicaciones", "bauh", "pirut.svg"),
            ("Ventana de inicio de sesión", "pkexec lightdm-settings", "launch.svg")
        ])

        # Sección: Internet and Wireless
        self.crear_seccion(main_box, "Conexiones", "Configuración de conexiones de red y dispositivos inalámbricos", "conn.svg", [
            ("Conexiones de Red", "nm-connection-editor", "network-wired.svg"),
            ("Adaptadores Bluetooth", "blueman-adapters", "adp_b.svg"),
            ("Dispositivos Bluetooth", "blueman-manager", "bluetooth.svg"),
        ])
        
        # Sección: Energy
        self.crear_seccion(main_box, "Energia", "Opciones de gestión de energía y preferencias de salvapantallas", "energy.svg", [
            ("Gestion de energia", "xfce4-power-manager-settings", "xfce4-battery-plugin.svg"),
            ("Salvapantallas", "xfce4-screensaver-preferences", "screensaver.svg"),
        ])
        
        # Sección: Hardware and Sound
        self.crear_seccion(main_box, "Hardware", "Configuración de hardware y dispositivos de sonido", "hardware.svg", [
            ("Configuracion de servicios de impresora", "sakura -e pkexec cups-switch", "printer.svg"),
            ("Instalador de controladores NVIDIA", "sakura -e pkexec nvidia_installer", "nvidia.svg"),
            ("Audio", "pavucontrol", "audio-volume-high.svg"),
            ("Ecualizador (Pipewire)", "jamesdsp", "equalizer.svg"),
            ("Pantalla (X11/Xorg)", "arandr", "x11.svg"),
            ("Pantalla (Wayland)", "wdisplays", "way.svg"),
            ("Almacenamiento", "gnome-disks", "disk-utility.svg"),
            ("Informacion de Hardware", "hardinfo", "hwinfo.svg")
        ])

        # Sección: Users and Groups
        self.crear_seccion(main_box, "Accesibilidad", "Opciones de accesibilidad y configuración de usuarios", "accs.svg", [
            ("Controlar los usuarios o grupos", "users-admin", "user.svg"),
            ("Programas predeterminados", os.path.join(os.getcwd(), "tools", "mime"), "application-x-m4.svg"),
            ("Teclado", "ibus", "keys.svg"),
            ("Gestion de Hora/Fecha", "time-admin", "clock.svg"),
            ("Calendario", "orage", "calendar.svg"),
        ])

        # Sección: Customization
        self.crear_seccion(main_box, "Personalización", "Opciones para personalizar la apariencia del sistema", "preferences-desktop-theme.svg", [
            ("Conkyman", "/usr/share/conkyman/conkyman.py", "conkyman.svg"),
            ("Fondo de pantalla", "nitrogen", "image.svg"),
            ("Fuentes de Texto", "font-manager", "fonts.svg"),
            ("Personalizar apariencia de Qt", "qt5ct", "qt.svg"),
            ("Personalizar apariencia de GTK", "nwg-look", "preferences-desktop-theme-global.svg"),
        ])
            
        # Sección: Avanced
        self.crear_seccion(main_box, "Archivos de Configuración", "Acceso rápido a archivos de configuración", "text-editor.svg", [
            ("Archivo de config. de sway", "xdg-open ~/.config/sway/config", "sway.svg"),
            ("Archivo de config. de i3", "xdg-open ~/.config/i3/config", "i3.svg"),
            ("Archivo de config. de awesome", "xdg-open ~/.config/awesome/rc.lua", "awesome.svg")
        ])

        # Agregar el contenedor principal al contenedor de desplazamiento
        scrolled_window.add(main_box)

        # Agregar el contenedor principal a la ventana
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        window_box.pack_start(menu_bar, False, False, 0)
        window_box.pack_start(scrolled_window, True, True, 0)

        # Agregar el contenedor a la ventana
        self.add(window_box)

    def crear_seccion(self, parent_box, titulo, descripcion, icono_seccion, botones):
        # Crear un contenedor para la sección
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        section_box.set_margin_start(20)
        section_box.set_margin_end(20)
        section_box.set_margin_top(5)
        section_box.set_margin_bottom(10)
        section_box.set_hexpand(True)
        section_box.set_vexpand(True)

        # Crear un contenedor horizontal para el título y el icono
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        icon_path = os.path.join(os.getcwd(), "/usr/share/cuerd_settings/ico", icono_seccion)
        icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 24, 24))
        title_box.pack_start(icon, False, False, 0)

        # Crear un título para la sección
        section_label = Gtk.Label(label=f"<b>{titulo}</b>")
        section_label.set_justify(Gtk.Justification.LEFT)
        section_label.set_use_markup(True)
        section_label.set_halign(Gtk.Align.START)
        title_box.pack_start(section_label, False, False, 0)

        # Agregar el contenedor del título a la sección
        section_box.pack_start(title_box, False, False, 0)

        # Crear una etiqueta para la descripción
        description_label = Gtk.Label(label=descripcion)
        description_label.set_justify(Gtk.Justification.LEFT)
        description_label.set_halign(Gtk.Align.START)
        section_box.pack_start(description_label, False, False, 0)

        # Crear un Grid para los botones
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_hexpand(True)
        grid.set_vexpand(True)

        # Calcular el tamaño de la cuadrícula
        num_buttons = len(botones)
        grid_size = int(num_buttons**0.5)  # Calcular el tamaño del lado del cuadrado más cercano
        if grid_size**2 < num_buttons:
            grid_size += 1

        # Agregar botones al Grid
        for i, (label, command, icon_name) in enumerate(botones):
            button = Gtk.Button(label=label)
            
            # Configurar el icono con el tamaño 18x18
            icon_path = os.path.join(os.getcwd(), "/usr/share/cuerd_settings/ico", icon_name)
            icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 18, 18))
            button.set_image(icon)
            button.set_always_show_image(True)
            
            # Establecer hexpand y vexpand para los botones
            button.set_hexpand(True)
            button.set_vexpand(True)
            button.set_size_request(100, 40)  # Aumentar la altura de los botones
            button.connect("clicked", self.on_button_clicked, command)
            grid.attach(button, i % grid_size, i // grid_size, 1, 1)

        section_box.pack_start(grid, True, True, 0)
        parent_box.pack_start(section_box, False, False, 0)

    def on_button_clicked(self, widget, command):  # pylint: disable=unused-argument
        # Crear un hilo para ejecutar el comando en segundo plano
        threading.Thread(target=self.run_command, args=(command,)).start()

    def run_command(self, command):
        # Ejecutar el comando en un hilo separado
        try:
            if command.startswith("xdg-open"):
                subprocess.run(command, shell=True, check=True)
            else:
                subprocess.run(command, shell=True, check=True)
            print(f"Comando ejecutado: {command}")
        except subprocess.CalledProcessError as e:
            # Si el comando es qt5ct, no mostrar el mensaje de error
            if 'qt5ct' in command:
                print(f"Error ejecutando el comando {command}: {e}")
            else:
                print(f"Error ejecutando el comando {command}: {e}")
                self.show_error_dialog(f"El comando no se pudo ejecutar: {command}")
        except FileNotFoundError:
            print(f"Comando no encontrado: {command}")
            self.show_error_dialog(f"El programa no se encontró: {command}")
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            self.show_error_dialog(f"Ocurrió un error: {e}")

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.format_secondary_text(
            "Por favor, verifique que el programa esté instalado y accesible."
        )
        dialog.run()
        dialog.destroy()

    def show_about_dialog(self, widget):  # pylint: disable=unused-argument
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("Ajustes de CuerdOS")
        about_dialog.set_version("1.0 v090125b Elena")
        about_dialog.set_comments("Panel de control exclusivo para CuerdOS GNU/Linux.")
        about_dialog.set_website("https://github.com/CuerdOS")
        about_dialog.set_website_label("GitHub")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)

        # Ruta del logo
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
