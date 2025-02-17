import os
import subprocess
import threading
import gi
import json
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
        icon_path = self.find_icon_path(current_dir, "/usr/share/cuerd_settings/icons/settings")

        # Si se encuentra el archivo, configuramos el icono para la ventana y para la barra de tareas
        if icon_path:
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            self.set_icon(icon_pixbuf)  # Establece el icono para la ventana
            self.set_default_icon_from_file(icon_path)  # Establece el icono para la barra de tareas

        # Barra de menús
        menu_bar = Gtk.MenuBar()

        # Menú "Ayuda"
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="Ayuda")
        file_item.set_submenu(file_menu)

        acerca_item = Gtk.MenuItem(label="Acerca de...")
        acerca_item.connect("activate", self.show_about_dialog)
        file_menu.append(acerca_item)

        # Menú "Configuración"
        settings_menu = Gtk.Menu()
        settings_item = Gtk.MenuItem(label="Configuración")
        settings_item.set_submenu(settings_menu)

        icon_pack_item = Gtk.MenuItem(label="Elegir paquete de iconos")
        icon_pack_item.connect("activate", self.show_icon_pack_dialog)
        settings_menu.append(icon_pack_item)

        menu_bar.append(file_item)
        menu_bar.append(settings_item)

        # Contenedor principal con barra de desplazamiento
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)  # Deshabilitar desplazamiento horizontal

        # Crear un contenedor vertical para las secciones
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_vexpand(True)
        main_box.set_hexpand(True)

        # Cargar la configuración del paquete de iconos
        self.load_icon_pack_config()

        # Sección: System and Security
        self.crear_seccion(main_box, "Sistema y Seguridad", "Seguridad del sistema y configuración", "security-low", [
            ("Cortafuegos", "firewall-config", "fire"),
            ("Configuracion de Repositorios", "sakura -e pkexec setup-repos", "administration"),
            ("Limpiar el sistema", "bleachbit", "edit-clear-all"),
            ("Tienda de aplicaciones", "bauh", "pirut"),
            ("Ventana de inicio de sesión", "pkexec lightdm-settings", "launch")
        ])

        # Sección: Internet and Wireless
        self.crear_seccion(main_box, "Conexiones", "Configuración de conexiones de red y dispositivos inalámbricos", "conn", [
            ("Conexiones de Red", "nm-connection-editor", "network-wired"),
            ("Adaptadores Bluetooth", "blueman-adapters", "adp_b"),
            ("Dispositivos Bluetooth", "blueman-manager", "bluetooth"),
        ])
        
        # Sección: Energy
        self.crear_seccion(main_box, "Energia", "Opciones de gestión de energía y preferencias de salvapantallas", "energy", [
            ("Gestion de energia", "xfce4-power-manager-settings", "xfce4-battery-plugin"),
            ("Salvapantallas", "xfce4-screensaver-preferences", "screensaver"),
        ])
        
        # Sección: Hardware and Sound
        self.crear_seccion(main_box, "Hardware", "Configuración de hardware y dispositivos de sonido", "hardware", [
            ("Configuracion de servicios de impresora", "sakura -e pkexec cups-switch", "printer"),
            ("Instalador de controladores NVIDIA", "sakura -e pkexec nvidia_installer", "nvidia"),
            ("Audio", "pavucontrol", "audio-volume-high"),
            ("Ecualizador (Pipewire)", "jamesdsp", "equalizer"),
            ("Pantalla (X11/Xorg)", "arandr", "x11"),
            ("Pantalla (Wayland)", "wdisplays", "way"),
            ("Almacenamiento", "gnome-disks", "disk-utility"),
            ("Informacion de Hardware", "hardinfo", "hwinfo")
        ])

        # Sección: Users and Groups
        self.crear_seccion(main_box, "Accesibilidad", "Opciones de accesibilidad y configuración de usuarios", "accs", [
            ("Controlar los usuarios o grupos", "users-admin", "user"),
            ("Programas predeterminados", os.path.join(os.getcwd(), "tools", "mime"), "application-x-m4"),
            ("Teclado", "ibus", "keys"),
            ("Gestion de Hora/Fecha", "time-admin", "clock"),
            ("Calendario", "orage", "calendar"),
        ])

        # Sección: Customization
        self.crear_seccion(main_box, "Personalización", "Opciones para personalizar la apariencia del sistema", "preferences-desktop-theme", [
            ("Conkyman", "/usr/share/conkyman/conkyman.py", "conkyman"),
            ("Fondo de pantalla", "nitrogen", "image"),
            ("Fuentes de Texto", "font-manager", "fonts"),
            ("Personalizar apariencia de Qt", "qt5ct", "qt"),
            ("Personalizar apariencia de GTK", "nwg-look", "preferences-desktop-theme-global"),
        ])
            
        # Sección: Avanced
        self.crear_seccion(main_box, "Archivos de Configuración", "Acceso rápido a archivos de configuración", "text-editor", [
            ("Archivo de config. de sway", "xdg-open ~/.config/sway/config", "sway"),
            ("Archivo de config. de i3", "xdg-open ~/.config/i3/config", "i3"),
            ("Archivo de config. de awesome", "xdg-open ~/.config/awesome/rc.lua", "awesome")
        ])

        # Agregar el contenedor principal al contenedor de desplazamiento
        scrolled_window.add(main_box)

        # Agregar el contenedor principal a la ventana
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        window_box.pack_start(menu_bar, False, False, 0)
        window_box.pack_start(scrolled_window, True, True, 0)

        # Agregar el contenedor a la ventana
        self.add(window_box)

    def find_icon_path(self, base_dir, icon_name):
        """Buscar el archivo de icono con extensión .svg o .png"""
        for ext in [".svg", ".png"]:
            path = os.path.join(base_dir, icon_name + ext)
            if os.path.exists(path):
                return path
        return None

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
        icon_path = self.find_icon_path(f"/usr/share/cuerd_settings/ico/{self.icon_pack}", icono_seccion)
        
        # Verificar la existencia del archivo antes de cargarlo
        if icon_path:
            icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 24, 24))
        else:
            print(f"Archivo de icono no encontrado: {icon_path}")
            icon = Gtk.Image()  # Crear un objeto Gtk.Image vacío en caso de que no se encuentre el archivo
        
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
            icon_path = self.find_icon_path(f"/usr/share/cuerd_settings/ico/{self.icon_pack}", icon_name)
            if icon_path:
                icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 18, 18))
            else:
                print(f"Archivo de icono no encontrado: {icon_path}")
                icon = Gtk.Image()  # Crear un objeto Gtk.Image vacío en caso de que no se encuentre el archivo
            
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
        about_dialog.set_version("1.0 v300125a Elena")
        about_dialog.set_comments("Panel de control exclusivo para CuerdOS GNU/Linux.")
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

        # Ruta del logo
        current_dir = os.getcwd()
        logo_path = self.find_icon_path(current_dir, "/usr/share/cuerd_settings/icons/settings_about")

        if logo_path:
            logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file(logo_path)
            logo_pixbuf = logo_pixbuf.scale_simple(150, 150, GdkPixbuf.InterpType.BILINEAR)
            about_dialog.set_logo(logo_pixbuf)

        about_dialog.run()
        about_dialog.destroy()

    def show_icon_pack_dialog(self, widget):  # pylint: disable=unused-argument
        dialog = Gtk.Dialog(title="Elegir paquete de iconos", transient_for=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        box = dialog.get_content_area()
        label = Gtk.Label(label="Seleccione un paquete de iconos:")
        box.add(label)

        icon_pack_store = Gtk.ListStore(str)
        
        # Detectar carpetas de paquetes de iconos y archivos .png o .svg
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
        
        # Seleccionar por defecto "CuerdOS-Elementary"
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
        print(f"Configuración del paquete de iconos guardada: {icon_pack}")

    def load_icon_pack_config(self):
        config_path = os.path.join(os.getcwd(), "icon_pack_config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                self.icon_pack = config.get("icon_pack", "CuerdOS-Elementary")
                print(f"Configuración del paquete de iconos cargada: {self.icon_pack}")
        else:
            self.icon_pack = "CuerdOS-Elementary"
            print("No se encontró ninguna configuración del paquete de iconos. Usando 'CuerdOS-Elementary' por defecto.")

def main():
    win = ControlPanel()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()