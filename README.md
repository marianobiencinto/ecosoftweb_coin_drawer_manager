# Coin Drawer Manager (Gestor del Cajón Portamonedas TPV)

Este proyecto está diseñado **exclusivamente para sistemas macOS**. Permite abrir automáticamente un cajón portamonedas conectado a una impresora de tickets mediante peticiones HTTP desde el navegador (por ejemplo, desde la web de Ecosoft), utilizando un script de Tampermonkey y un servidor local en Python.

---

## Requisitos del Sistema

Para poder utilizar esta herramienta, tu equipo debe cumplir con los siguientes requisitos:

1. **Sistema Operativo:** macOS (OS X / macOS Catalina, Big Sur, Monterey, Ventura, Sonoma, Sequoia o superior).
2. **Python 3:** Debe estar instalado en el sistema (por lo general viene preinstalado, o se puede instalar usando Homebrew o el sitio web oficial de Python).
3. **Impresora POS/Tickets:** Una impresora térmica de tickets (con soporte ESC/POS) configurada y reconocida en el sistema (instalada en el panel de macOS *Ajustes del Sistema -> Impresoras y escáneres*).
4. **Cajón Portamonedas:** Debe estar conectado físicamente a la impresora de tickets a través del puerto telefónico RJ11.
5. **Navegador Web:** Un navegador moderno (Chrome, Firefox, Safari, Edge, etc.) con la extensión **Tampermonkey** instalada.

---

## 1. Configuración del Servidor

El servidor se comunica con la impresora del sistema mediante los comandos nativos de impresión de macOS (`lp` y `lpstat`).

1. **Obtener las impresoras instaladas:**
   Abre una terminal y ejecuta el siguiente comando para ver el nombre exacto de tus impresoras:
   ```bash
   lpstat -p
   ```
   *Nota: Verás líneas como `la impresora Brother_HL_L2300D_series está inactiva...`.*

2. **Configurar el archivo `config.json`:**
   Abre el archivo `config.json` en este directorio y actualiza la propiedad `"printer_name"` con el nombre exacto de la impresora donde tienes conectado el cajón:
   ```json
   {
       "host": "127.0.0.1",
       "port": 6543,
       "endpoint": "/open-drawer",
       "printer_name": "TU_IMPRESORA_AQUÍ",
       "drawer_sequence": "\\x1B\\x70\\x00\\x19\\xFA",
       "cors_origin": "*"
   }
   ```

---

## 2. Configurar Inicio Automático en macOS (Servicio launchd)

Para que el servidor se ejecute en segundo plano automáticamente cada vez que inicies sesión en tu Mac:

1. **Editar el archivo `.plist` para ajustar las rutas:**
   Abre el archivo [com.ecosoft.coindrawer.plist](file:///Users/pawboss/Desktop/marianobiencinto.dev/projects/ecosoft/ecosoftweb_coin_drawer_manager/com.ecosoft.coindrawer.plist) y asegúrate de modificar los placeholders con las rutas reales de tu sistema:
   - `/ruta/a/tu/python3`: La ruta al ejecutable de Python 3 de tu sistema (puedes obtenerla ejecutando `which python3` en la terminal, ej: `/usr/bin/python3`, `/usr/local/bin/python3` o `/opt/homebrew/bin/python3`).
   - `/ruta/a/la/carpeta/del/proyecto`: La ruta absoluta donde se encuentra este proyecto (ej: `/Users/tu_usuario/ruta/del/proyecto`).

2. **Copiar el archivo de configuración del servicio:**
   Desde la terminal del proyecto, copia el archivo `com.ecosoft.coindrawer.plist` a la carpeta de LaunchAgents del usuario:
   ```bash
   cp com.ecosoft.coindrawer.plist ~/Library/LaunchAgents/
   ```

3. **Cargar y arrancar el servicio:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.ecosoft.coindrawer.plist
   ```

### Comandos de gestión del servicio:
* **Detener el servicio:**
  ```bash
  launchctl unload ~/Library/LaunchAgents/com.ecosoft.coindrawer.plist
  ```
* **Reiniciar el servicio (si cambias la configuración en config.json):**
  ```bash
  launchctl unload ~/Library/LaunchAgents/com.ecosoft.coindrawer.plist
  launchctl load ~/Library/LaunchAgents/com.ecosoft.coindrawer.plist
  ```
* **Ver registros de errores / logs:**
  Cualquier salida o error del servidor se guardará automáticamente en el archivo `server.log` del proyecto.

---

## 3. Instalación y Configuración de Tampermonkey

Para vincular las acciones de la web de Ecosoft con tu cajón local:

1. **Instalar Tampermonkey:**
   Instala la extensión Tampermonkey en tu navegador web desde su tienda de extensiones oficial.

2. **Crear un nuevo script:**
   * Abre el panel de control de Tampermonkey haciendo clic en el icono de la extensión y selecciona **Crear un nuevo script** (o el botón "+").
   * Copia todo el contenido del archivo `browser_script.js` de este proyecto.
   * Pégalo en el editor de Tampermonkey reemplazando el código que venga por defecto.
   * Guarda el script (Menú *Archivo -> Guardar* o `Ctrl+S` / `Cmd+S`).

3. **Verificar el funcionamiento:**
   * Entra en tu panel de ventas/TPV de Ecosoft (`https://ecosoftweb.net/`).
   * El script de Tampermonkey detectará automáticamente los botones con clases `.open_drawer` o `.finish`.
   * Al hacer clic en cualquiera de estos botones (por ejemplo, al finalizar una venta), se enviará una petición local al servidor local `http://127.0.0.1:6543/open-drawer` que activará la apertura del cajón portamonedas.
