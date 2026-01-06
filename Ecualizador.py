"""
PROYECTO: Ecualizador de Audio Multibanda + Espectrograma
ASIGNATURA: Matemáticas Avanzadas para la Ingenieria
Elaborado por:
Molina Flores Sebastian
Rozas Lezama Carlos
Valencia Reséndiz Carlos Alfonso
DESCRIPCIÓN:
    Aplicación de escritorio para mezclar dos pistas de audio, aplicar un filtro
    de ecualización de 5 bandas utilizando la Transformada de Fourier (FFT) y
    visualizar los resultados en tiempo real (Onda y Espectrograma).
"""

import tkinter as tk
from tkinter import ttk, Button, filedialog, messagebox
import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import soundfile as sf  # Librería para guardar el audio procesado


class EqualizerApp(tk.Tk):
    """
    Clase principal de la interfaz gráfica.
    Gestiona la carga de archivos, el procesamiento matemático y la visualización.
    """

    def __init__(self):
        super().__init__()
        self.title("Ecualizador Multibanda (Gestión de Pistas)")
        self.geometry("1100x750")
        self.ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")

        # --- Variables del Sistema de Audio ---
        self.y_original = None  # Señal combinada (Mezcla de Audio 1 + Audio 2)
        self.sr = None  # Frecuencia de muestreo (Sample Rate)
        self.y_modificado = None  # Señal resultante después del filtro (IFFT)
        self.fft_original = None  # Transformada de Fourier de la señal original
        self.freqs = None  # Eje de frecuencias correspondiente a la FFT

        # Almacenamiento de pistas individuales
        self.y1 = None  # Pista 1 (Base/Voz)
        self.y2 = None  # Pista 2 (Fondo/Ruido)

        #  INTERFAZ GRÁFICA (GUI)

        # Panel de control superior
        ctrl_frame = tk.Frame(self, bg="#eee", pady=10)
        ctrl_frame.pack(side=tk.TOP, fill="x")

        # --- GRUPO 1: AUDIO BASE ---
        frame_1 = tk.Frame(ctrl_frame, bg="#eee")
        frame_1.pack(side=tk.LEFT, padx=5)

        btn_load1 = Button(frame_1, text="1. Cargar Voz", bg="#4CAF50", fg="white",
                           font=("Arial", 9, "bold"), command=lambda: self.cargar_un_audio(1))
        btn_load1.pack(side=tk.LEFT)

        # Botón para eliminar Audio 1
        btn_del1 = Button(frame_1, text="X", bg="#E53935", fg="white", width=2,
                          font=("Arial", 8, "bold"), command=lambda: self.eliminar_audio(1))
        btn_del1.pack(side=tk.LEFT, padx=2)

        # --- GRUPO 2: AUDIO FONDO ---
        frame_2 = tk.Frame(ctrl_frame, bg="#eee")
        frame_2.pack(side=tk.LEFT, padx=5)

        btn_load2 = Button(frame_2, text="2. Cargar Fondo", bg="#FF9800", fg="white",
                           font=("Arial", 9, "bold"), command=lambda: self.cargar_un_audio(2))
        btn_load2.pack(side=tk.LEFT)

        # Botón para eliminar Audio 2
        btn_del2 = Button(frame_2, text="X", bg="#E53935", fg="white", width=2,
                          font=("Arial", 8, "bold"), command=lambda: self.eliminar_audio(2))
        btn_del2.pack(side=tk.LEFT, padx=2)

        # Etiqueta de estado
        self.lbl_status = tk.Label(ctrl_frame, text="Esperando audios...", bg="#eee", font=("Arial", 9))
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        # --- BOTONES DE ACCIÓN ---
        btn_save = Button(ctrl_frame, text="💾 Guardar", bg="#008CBA", fg="white",
                          font=("Arial", 10, "bold"), command=self.guardar_archivo)
        btn_save.pack(side=tk.RIGHT, padx=15)

        btn_apply = Button(ctrl_frame, text="🔄 Actualizar Gráficos", bg="#2196F3", fg="white",
                           font=("Arial", 10, "bold"), command=self.aplicar_filtro)
        btn_apply.pack(side=tk.RIGHT, padx=5)

        # --- SLIDERS ---
        slider_frame = tk.LabelFrame(self, text="Ecualizador (Ajusta y pulsa 'Actualizar')", padx=10, pady=10)
        slider_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        self.sliders = []
        # Definición de las 5 bandas de frecuencia
        self.bandas_info = ["Sub-Bajos\n(0-60Hz)", "Bajos\n(60-250Hz)", "Medios\n(250-2k)", "Agudos\n(2k-4k)",
                            "Brillo\n(4k+)"]

        for i in range(5):
            frame_s = tk.Frame(slider_frame)
            frame_s.pack(side=tk.LEFT, expand=True, fill="x")

            # Slider vertical. Valor 1.0 = Ganancia unitaria (sin cambio).
            s = tk.Scale(frame_s, from_=3.0, to=0.0, resolution=0.1, orient="vertical", length=120)
            s.set(1.0)
            s.pack()

            lbl = tk.Label(frame_s, text=self.bandas_info[i], font=("Arial", 8))
            lbl.pack()
            self.sliders.append(s)

        # --- ÁREA DE VISUALIZACIÓN (MATPLOTLIB) ---
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax_wave = self.fig.add_subplot(211)  # Gráfico superior (Onda)
        self.ax_spec = self.fig.add_subplot(212)  # Gráfico inferior (Espectrograma)
        self.fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # LÓGICA DE GESTIÓN DE ARCHIVOS

    def cargar_un_audio(self, slot):
        """
        Abre un diálogo para cargar un archivo de audio (.wav/.mp3).

        Args:
            slot (int): 1 para Audio Base, 2 para Audio Fondo.
        """
        ruta = filedialog.askopenfilename(parent=self,
                                          title=f"Seleccionar Audio {slot}",
                                          initialdir=self.ruta_descargas,
                                          filetypes=[("Archivos de Audio", "*.wav *.mp3")])
        if not ruta: return

        try:
            # --- CARGA DEL SLOT 1 (BASE) ---
            if slot == 1 or self.sr is None:
                # librosa.load devuelve: señal de audio (y1) y frecuencia de muestreo (sr)
                self.y1, self.sr = librosa.load(ruta, sr=None, duration=30)
                self.y1 = self.y1.astype(np.float32)  # Conversión a float32 para optimizar

                nombre = ruta.split('/')[-1]
                self.lbl_status.config(text=f"Cargado 1: {nombre}")

                # Al cambiar la base, el audio 2 puede quedar incompatible (diferente SR), se reinicia.
                if slot == 1 and self.y2 is not None:
                    self.y2 = None
                    messagebox.showinfo("Aviso", "Se reinició el Audio 2 al cambiar la base.")

            # --- CARGA DEL SLOT 2 (FONDO) ---
            elif slot == 2:
                if self.y1 is None:
                    messagebox.showwarning("Orden", "Carga el audio 1 primero para definir la frecuencia base.")
                    return
                # Importante: Forzamos sr=self.sr para que coincida con el audio 1
                self.y2, _ = librosa.load(ruta, sr=self.sr, duration=30)
                self.y2 = self.y2.astype(np.float32)
                nombre = ruta.split('/')[-1]
                self.lbl_status.config(text=f"Mezclado con: {nombre}")

            # Una vez cargado, procesamos la mezcla
            self.mezclar_y_procesar()

        except Exception as e:
            messagebox.showerror("Error crítico", str(e))

    def eliminar_audio(self, slot):
        """Elimina el audio del slot seleccionado y actualiza el estado del sistema."""
        if slot == 1:
            # Eliminar Audio 1 implica reiniciar todo el sistema (es la referencia)
            self.y1 = None
            self.y2 = None
            self.sr = None
            self.y_original = None
            self.y_modificado = None
            self.fft_original = None

            # Limpiar gráficos y resetear sliders
            self.ax_wave.clear()
            self.ax_spec.clear()
            self.canvas.draw()
            for s in self.sliders: s.set(1.0)

            self.lbl_status.config(text="Audio 1 eliminado. Sistema reiniciado.")

        elif slot == 2:
            # Eliminar Audio 2 solo requiere volver a procesar el Audio 1 solo
            if self.y2 is not None:
                self.y2 = None
                self.lbl_status.config(text="Audio 2 eliminado. Solo queda Audio 1.")
                self.mezclar_y_procesar()
            else:
                messagebox.showinfo("Info", "No hay Audio 2 cargado.")

    def mezclar_y_procesar(self):
        """
        Combina las señales y1 y y2 (si existen), calcula la FFT inicial
        y prepara el sistema para filtrar.
        """
        if self.y1 is None: return

        # Comenzamos con la copia del Audio 1
        mezcla = self.y1.copy()

        # Si existe Audio 2, realizamos la mezcla
        if self.y2 is not None:
            # Igualamos longitudes usando zero-padding (rellenar con ceros)
            max_len = max(len(self.y1), len(self.y2))
            y1_pad = librosa.util.fix_length(self.y1, size=max_len)
            y2_pad = librosa.util.fix_length(self.y2, size=max_len)

            # Promedio simple para evitar saturación (clipping)
            mezcla = (y1_pad + y2_pad) * 0.5

        self.y_original = mezcla

        # --- CÁLCULO MATEMÁTICO (FFT) ---
        # Llevamos la señal del dominio del tiempo al dominio de la frecuencia
        self.fft_original = np.fft.rfft(self.y_original)

        # Obtenemos el vector de frecuencias asociado
        self.freqs = np.fft.rfftfreq(len(self.y_original), 1 / self.sr)

        # Reseteamos los sliders a ganancia 1.0 (neutro) al cargar nuevo audio
        for s in self.sliders: s.set(1.0)

        # Aplicamos el filtro (inicialmente plano)
        self.aplicar_filtro()

    # PROCESAMIENTO DE SEÑALES Y FILTRADO

    def aplicar_filtro(self):
        """
        Construye una máscara de filtrado basada en los sliders, multiplica
        en frecuencia y reconstruye el audio (IFFT).
        Se ejecuta al pulsar 'Actualizar Gráficos'.
        """
        if self.fft_original is None: return

        # Obtener valores de ganancia de la GUI
        ganancias = [s.get() for s in self.sliders]

        # Crear máscara (filtro) inicializada en 1 (sin cambio)
        mascara = np.ones_like(self.fft_original, dtype=float)

        # Definición de límites de banda en Hz
        limites = [0, 60, 250, 2000, 4000, self.sr / 2]

        # Aplicar ganancia a cada rango de frecuencia
        for i in range(5):
            g = ganancias[i]
            # Buscamos qué índices del array 'freqs' caen en esta banda
            indices = np.where((self.freqs >= limites[i]) & (self.freqs < limites[i + 1]))
            # Multiplicamos esos índices por la ganancia del slider
            mascara[indices] *= g

        # Filtrado: Multiplicación en el Dominio de la Frecuencia
        fft_filtrada = self.fft_original * mascara

        # Reconstrucción: Transformada Inversa de Fourier (IFFT)
        self.y_modificado = np.fft.irfft(fft_filtrada)

        # Actualizar visualización
        self.graficar()

    def graficar(self):
        """Genera las gráficas de Onda y Espectrograma."""
        self.ax_wave.clear()
        self.ax_spec.clear()

        # --- Gráfico 1: Dominio del Tiempo ---
        # Optimizacion: 'step' reduce puntos para dibujar más rápido
        step = max(1, len(self.y_modificado) // 5000)
        tiempos = np.linspace(0, len(self.y_modificado) / self.sr, num=len(self.y_modificado))

        self.ax_wave.plot(tiempos[::step], self.y_modificado[::step], color='#007acc', linewidth=0.5)
        self.ax_wave.set_title("Señal Resultante (Dominio del Tiempo)")
        self.ax_wave.set_ylabel("Amplitud")
        self.ax_wave.set_ylim(-1, 1)
        self.ax_wave.grid(True, alpha=0.3)

        # --- Gráfico 2: Espectrograma (Tiempo-Frecuencia) ---
        # Cálculo de la STFT (Short-Time Fourier Transform) para visualización
        D = librosa.amplitude_to_db(np.abs(librosa.stft(self.y_modificado)), ref=np.max)
        librosa.display.specshow(D, sr=self.sr, x_axis='time', y_axis='log', ax=self.ax_spec, cmap='magma')
        self.ax_spec.set_title("Espectrograma")
        self.ax_spec.set_ylabel("Frecuencia (Hz)")

        self.canvas.draw()

    def guardar_archivo(self):
        """Exporta el audio procesado a un archivo .WAV."""
        if self.y_modificado is None:
            messagebox.showwarning("Alerta", "No hay audio para guardar.")
            return

        ruta = filedialog.asksaveasfilename(parent=self,
                                            title="Guardar Audio Resultante",
                                            initialdir=self.ruta_descargas,  # Usa carpeta Descargas
                                            defaultextension=".wav",
                                            filetypes=[("WAV", "*.wav")])
        if ruta:
            try:
                sf.write(ruta, self.y_modificado, self.sr)
                messagebox.showinfo("Éxito", f"Archivo guardado correctamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error al guardar", str(e))


if __name__ == "__main__":
    app = EqualizerApp()
    app.mainloop()