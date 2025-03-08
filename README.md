# PowerTimer - Temporizador de Apagado

PowerTimer es una aplicación de línea de comandos escrita en Python que permite programar el apagado automático de tu computadora con una interfaz estilizada y personalizable. Diseñada para ser multiplataforma (Windows, Linux, macOS), ofrece una experiencia interactiva con navegación por menú, soporte para temas, sonidos de notificación y opciones avanzadas como pausar/reanudar el temporizador.

## Características

- **Temporizador configurable**: Opciones predefinidas (30 min, 1 hora, 2 horas) o tiempo personalizado.
- **Interfaz estilizada**: Diseño en terminal con bordes decorativos, colores y barra de progreso.
- **Navegación intuitiva**: Usa las teclas de flecha (↑↓) y Enter para seleccionar opciones.
- **Temas personalizables**: Elige entre temas como `dark`, `light` y `retro`, con opción de cambiarlos desde la interfaz.
- **Soporte para pausa**: Pausa y reanuda el temporizador con la tecla 'P'.
- **Notificaciones audibles**: Sonidos al iniciar, pausar, cancelar o completar el temporizador.
- **Configuración persistente**: Guarda los tiempos usados recientemente y el tema seleccionado en un archivo JSON.
- **Multiplataforma**: Compatible con Windows, Linux y macOS (con ajustes para sonidos en UNIX).

## Requisitos

- **Python 3.6+**: Asegúrate de tener Python instalado.
- **Terminal compatible con ANSI**: Recomendado Windows Terminal o PowerShell en Windows, y cualquier terminal en Linux/macOS.
- **Permisos administrativos**: Necesarios para ejecutar el comando de apagado del sistema.
- **Opcional (Linux/macOS)**: Instala `beep` para sonidos avanzados (`sudo apt-get install beep` en Ubuntu).

## Instalación

1. **Descarga el programa**:
   - Clona el repositorio o descarga el archivo `powertimer.py`:
     ```bash
     git clone https://github.com/ImJustSebas/Windows-sleep-timer
     cd powertimer
