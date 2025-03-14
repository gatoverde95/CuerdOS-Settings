#!/bin/bash

# Detectar idioma del sistema
LANGUAGE=$(echo $LANG | cut -d'_' -f1)

# Decidir qué script ejecutar
if [ "$LANGUAGE" == "es" ]; then
    python3 /usr/share/cuerd_settings/settings.py
elif [ "$LANGUAGE" == "en" ]; then
    python3 /usr/share/cuerd_settings/settings_en.py
else
    echo "Idioma no soportado: $LANGUAGE"
    # Puedes establecer un script por defecto o mostrar un mensaje de error
    python3 /usr/share/cuerd_settings/settings.py  # Por defecto a español
fi

