# Ecualizador-de-audio-multi-banda
Proyecto Elaborado por:
-Molina Flores Sebastiasn
-Rosas Lezama Carlos
-Valencia Reséndiz Carlos Alfonso

# Requisitos del Sistema
Para ejecutar este programa es necesario tener instalado Python 3.8 o superior.
Las dependencias externas requeridas son:
-numpy: Para operaciones matemáticas y manejo de arrays.
-matplotlib: Para la generación de gráficas (onda y espectrograma).
-librosa: Para el análisis de audio y cálculo de STFT.
-soundfile: Para guardar el audio procesado.
-tkinter: Para la interfaz gráfica de usuario (incluido generalmente con Python).

# Instalación
1.-Asegúrate de tener Python instalado en tu equipo.
2.-Abre tu terminal o consola de comandos en la carpeta del proyecto.
3.-Instala las librerías necesarias ejecutando el siguiente comando:
pip install numpy matplotlib librosa soundfile

# Ejecución
Una vez instaladas las dependencias, puedes iniciar la aplicación ejecutando:
python Ecualizador.py

# Guía de Uso
1.-Cargar Audios:
  -Utiliza el botón "1. Cargar Voz" para seleccionar tu audio principal.
  -Utiliza el botón "2. Cargar Fondo" para añadir una pista secundaria o ruido. El programa las mezclará automáticamente.

2.-Ecualizar:
  -Mueve los sliders verticales para ajustar la ganancia de cada banda de frecuencia.
  -El gráfico se actualizará en tiempo real si mueves los controles, o puedes pulsar "Actualizar Gráficos" para forzar el redibujado.

3.-Analizar:
  -Observa la gráfica superior para ver cómo cambia la amplitud en el tiempo.
  -Observa el espectrograma inferior para ver la intensidad de las frecuencias a lo largo del tiempo.

4.-Guardar:
  -Presiona el botón "💾 Guardar" para exportar el resultado final a un archivo de audio.
