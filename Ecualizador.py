import tkinter as tk
from tkinter import ttk, Button, filedialog, messagebox
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class EqualizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ecualizador Multibanda + Espectrograma (FFT)")
        self.geometry("1000x700")

        # Variables globales para el audio
        self.y_original = None  # Audio original en el tiempo
        self.sr = None  # Frecuencia de muestreo
        self.y_modificado = None  # Audio procesado (después de la IFFT)
        self.fft_original = None  # Audio en frecuencia (números complejos)
        self.freqs = None  # Eje de frecuencias

        # --- 1. Panel de Control Superior ---
        ctrl_frame = tk.Frame(self, bg="#eee", pady=10)
        ctrl_frame.pack(side=tk.TOP, fill="x")

        btn_load = Button(ctrl_frame, text="1. Cargar Audio (.wav)", bg="#4CAF50", fg="white",
                          font=("Arial", 11, "bold"), command=self.cargar_archivo)
        btn_load.pack(side=tk.LEFT, padx=20)

        self.lbl_status = tk.Label(ctrl_frame, text="Sin archivo cargado", bg="#eee", font=("Arial", 10))
        self.lbl_status.pack(side=tk.LEFT)

        btn_apply = Button(ctrl_frame, text="Actualizar Gráficos", command=self.aplicar_filtro)
        btn_apply.pack(side=tk.RIGHT, padx=20)

        # --- 2. Área de Sliders (K=5 Bandas) ---
        # Frame para los sliders
        slider_frame = tk.LabelFrame(self, text="Control de Ganancia por Bandas (K=5)", padx=10, pady=10)
        slider_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        self.sliders = []
        self.bandas_info = ["Sub-Bajos\n(0-60Hz)", "Bajos\n(60-250Hz)", "Medios\n(250-2k)", "Agudos\n(2k-4k)",
                            "Brillo\n(4k+)"]

        # Creamos 5 sliders
        for i in range(5):
            frame_s = tk.Frame(slider_frame)
            frame_s.pack(side=tk.LEFT, expand=True, fill="x")

            # Slider vertical: Valor 1.0 es ganancia unitaria (sin cambio)
            # Rango de 0.0 (silencio) a 3.0 (triple amplitud)
            s = tk.Scale(frame_s, from_=3.0, to=0.0, resolution=0.1, orient="vertical", length=120)
            s.set(1.0)  # Valor por defecto
            s.pack()
            s.bind("<ButtonRelease-1>", self.al_soltar_slider)  # Actualizar solo al soltar para no trabar

            lbl = tk.Label(frame_s, text=self.bandas_info[i], font=("Arial", 8))
            lbl.pack()
            self.sliders.append(s)

        # --- 3. Área de Gráficos (Matplotlib) ---
        # Usamos subplots: Arriba Onda, Abajo Espectrograma
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax_wave = self.fig.add_subplot(211)  # 2 filas, 1 columna, gráfico 1
        self.ax_spec = self.fig.add_subplot(212)  # 2 filas, 1 columna, gráfico 2
        self.fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav *.mp3")])
        if ruta:
            try:
                # Cargar audio (limitado a 30s para que la FFT sea rápida en la demo)
                self.y_original, self.sr = librosa.load(ruta, sr=None, duration=30)

                self.lbl_status.config(text=f"Cargado: {ruta.split('/')[-1]} | {self.sr}Hz")

                # --- MATEMÁTICAS AVANZADAS (DFT/FFT) ---
                # Llevamos el audio al dominio de la frecuencia
                self.fft_original = np.fft.rfft(self.y_original)
                self.freqs = np.fft.rfftfreq(len(self.y_original), 1 / self.sr)

                # Inicializar audio modificado igual al original
                self.y_modificado = self.y_original.copy()

                # Graficar por primera vez
                self.graficar()

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def al_soltar_slider(self, event):
        """Se llama cuando el usuario suelta un slider"""
        self.aplicar_filtro()

    def aplicar_filtro(self):
        if self.fft_original is None:
            return

        # 1. Obtener valores de los sliders
        ganancias = [s.get() for s in self.sliders]

        # 2. Crear la máscara de filtro (Array de ganancias)
        # Inicializamos un filtro lleno de unos (que no hace nada)
        mascara = np.ones_like(self.fft_original, dtype=float)

        # Definir límites de las 5 bandas (en Hz)
        limites = [0, 60, 250, 2000, 4000, self.sr / 2]

        # 3. Aplicar ganancia a cada rango de frecuencia
        for i in range(5):
            g = ganancias[i]
            low_f = limites[i]
            high_f = limites[i + 1]

            # Buscar índices en el array de frecuencias que corresponden a esta banda
            indices = np.where((self.freqs >= low_f) & (self.freqs < high_f))

            # Aplicar la ganancia del slider a esos índices
            mascara[indices] *= g

        # 4. Multiplicación en Frecuencia (Convolución en tiempo)
        fft_filtrada = self.fft_original * mascara

        # 5. Transformada Inversa (IFFT) para recuperar el audio
        # irfft nos devuelve la señal en el tiempo (y_modificado)
        self.y_modificado = np.fft.irfft(fft_filtrada)

        # 6. Actualizar gráficos
        self.graficar()

    def graficar(self):
        # Limpiar ejes
        self.ax_wave.clear()
        self.ax_spec.clear()

        # --- GRÁFICO 1: Dominio del Tiempo (Onda) ---
        # Usamos downsampling [::100] para velocidad visual
        tiempos = np.linspace(0, len(self.y_modificado) / self.sr, num=len(self.y_modificado))
        self.ax_wave.plot(tiempos[::100], self.y_modificado[::100], color='#007acc', linewidth=0.5)
        self.ax_wave.set_title("Dominio del Tiempo (Señal Filtrada)")
        self.ax_wave.set_ylim(-1.5, 1.5)
        self.ax_wave.set_ylabel("Amplitud")
        self.ax_wave.grid(True, alpha=0.3)

        # --- GRÁFICO 2: Dominio de la Frecuencia (Espectrograma) ---
        # Calculamos el espectrograma (STFT) del audio MODIFICADO
        D = librosa.amplitude_to_db(np.abs(librosa.stft(self.y_modificado)), ref=np.max)

        img = librosa.display.specshow(D, sr=self.sr, x_axis='time', y_axis='log', ax=self.ax_spec, cmap='magma')
        self.ax_spec.set_title("Espectrograma (Evolución Frecuencial)")
        self.ax_spec.set_xlabel("Tiempo (s)")

        # Dibujar cambios
        self.canvas.draw()


if __name__ == "__main__":
    app = EqualizerApp()
    app.mainloop()