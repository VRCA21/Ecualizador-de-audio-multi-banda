# Ecualizador-de-audio-multi-banda
Proyecto Elaborado por:

- Molina Flores Sebastiasn
- Rosas Lezama Carlos
- Valencia Reséndiz Carlos Alfonso

# Requisitos del Sistema
Para ejecutar este programa es necesario tener instalado Python 3.8 o superior.

Las dependencias externas requeridas son:

- numpy: Para operaciones matemáticas y manejo de arrays.
- matplotlib: Para la generación de gráficas (onda y espectrograma).
- librosa: Para el análisis de audio y cálculo de STFT.
- soundfile: Para guardar el audio procesado.
- tkinter: Para la interfaz gráfica de usuario (incluido generalmente con Python).

# Instalación

1. Asegúrate de tener Python instalado en tu equipo.
2. Abre tu terminal o consola de comandos en la carpeta del proyecto.
3. Instala las librerías necesarias ejecutando el siguiente comando: pip install numpy matplotlib librosa soundfile

# Ejecución
Una vez instaladas las dependencias, puedes iniciar la aplicación ejecutando:

python Ecualizador.py

Para evitar conflictos con otras librerías y asegurar que el programa funcione correctamente, se recomienda utilizar un **entorno virtual**. Sigue estos pasos en tu terminal (CMD o PowerShell):

### 1. Crear el Entorno Virtual
Abre la terminal en la carpeta del proyecto y ejecuta:
python -m venv .venv

### 2. Activar el entorno

- En CMD:
.venv\Scripts\activate
- En PowerShell:
.venv\Scripts\Activate.ps1

# Guía de Uso
1. Cargar Audios:
  - Utiliza el botón "1. Cargar Voz" para seleccionar tu audio principal.
  - Utiliza el botón "2. Cargar Fondo" para añadir una pista secundaria o ruido. El programa las mezclará automáticamente.

2. Ecualizar:
  - Mueve los sliders verticales para ajustar la ganancia de cada banda de frecuencia.
  - El gráfico se actualizará en tiempo real si mueves los controles, o puedes pulsar "Actualizar Gráficos" para forzar el redibujado.

3. Analizar:
  - Observa la gráfica superior para ver cómo cambia la amplitud en el tiempo.
  - Observa el espectrograma inferior para ver la intensidad de las frecuencias a lo largo del tiempo.

4. Guardar:
  - Presiona el botón "💾 Guardar" para exportar el resultado final a un archivo de audio.
