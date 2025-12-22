import os, json, threading, queue
import multiprocessing as mp
import sys
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk

EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")

# Ruta para las fuentes: intenta carpeta local primero, luego Windows\Fonts
def obtener_ruta_fuentes():
    # Si está empaquetado con PyInstaller
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Prioridad: 1. fonts/ local, 2. Windows\Fonts
    ruta_local = os.path.join(base_path, "fonts")
    if os.path.exists(ruta_local):
        return ruta_local
    return r"C:\Windows\Fonts"

FUENTES_DIR = obtener_ruta_fuentes()

# ============ WORKER MULTIPROCESO ============

def worker_mp(args):
    """Worker que procesa una imagen individual"""
    ruta, salida, config = args
    try:
        # Abrir imagen
        img = Image.open(ruta).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Cargar fuente
        ruta_fuente = os.path.join(FUENTES_DIR, config["fuente"])
        if not os.path.exists(ruta_fuente):
            return ("ERR", ruta, f"Fuente no encontrada: {ruta_fuente}")
            
        fuente = ImageFont.truetype(ruta_fuente, config["tam"])

        texto = config["texto"]
        w, h = img.size
        bbox = draw.textbbox((0, 0), texto, font=fuente)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        m = config["margen"] if config["usar_margen"] else 0

        # Calcular posición
        pos = {
            "Arriba Izquierda": (m, m),
            "Arriba Derecha": (w-tw-m, m),
            "Abajo Izquierda": (m, h-th-m),
            "Abajo Derecha": (w-tw-m, h-th-m)
        }[config["pos"]]

        # Dibujar texto y guardar
        draw.text(pos, texto, fill=tuple(config["color"]), font=fuente)
        
        archivo_salida = os.path.join(salida, os.path.basename(ruta))
        img.save(archivo_salida, quality=95)

        return ("OK", ruta, archivo_salida)
    except Exception as e:
        import traceback
        return ("ERR", ruta, f"{str(e)}\n{traceback.format_exc()}")


# ==================== APP ====================

class FechadorApp:
    def __init__(self, root):
        self.root = root
        root.title("Fechador de Fotos PRO")
        root.geometry("1100x620")

        self.archivos = []
        self.idx = 0
        self.color = (255, 255, 255)

        self.texto = tk.StringVar(value="15/12/2025")
        self.origen = tk.StringVar()
        self.destino = tk.StringVar()
        self.fuente = tk.StringVar(value=self.cargar_fuentes()[0])
        self.tam = tk.IntVar(value=36)
        self.pos = tk.StringVar(value="Abajo Derecha")
        self.margen = tk.IntVar(value=20)
        self.usar_margen = tk.BooleanVar(value=True)
        self.modo_turbo = tk.BooleanVar(value=True)

        self.crear_ui()

    # ================= UI =================

    def crear_ui(self):
        main = tk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        self.panel = tk.Frame(main)
        self.panel.pack(side="left", fill="y", padx=10)

        self.preview = tk.Frame(main, bd=2, relief="groove")
        self.preview.pack(side="right", fill="both", expand=True, padx=10)

        self.ui_controles()
        self.ui_preview()

    def titulo(self, p, txt):
        tk.Label(p, text=txt, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))

    def ui_controles(self):
        p = self.panel

        self.titulo(p, "Origen")
        tk.Entry(p, textvariable=self.origen, width=40).pack()
        tk.Button(p, text="Carpeta", command=self.sel_dir).pack(fill="x")
        tk.Button(p, text="Fotos", command=self.sel_fotos).pack(fill="x")

        self.titulo(p, "Destino (opcional)")
        tk.Entry(p, textvariable=self.destino, width=40).pack()
        bf = tk.Frame(p)
        bf.pack(fill="x")
        tk.Button(bf, text="Seleccionar", command=self.sel_destino).pack(side="left", fill="x", expand=True)
        tk.Button(bf, text="Limpiar", command=lambda: self.destino.set("")).pack(side="left", fill="x", expand=True)
        tk.Label(p, text="(vacío = carpeta 'fechadas' en origen)", font=("Arial", 8), fg="gray").pack(anchor="w")

        self.titulo(p, "Texto")
        tk.Entry(p, textvariable=self.texto).pack(fill="x")

        self.titulo(p, "Color")
        cf = tk.Frame(p)
        cf.pack(anchor="w")
        tk.Button(cf, text="Elegir", command=self.elegir_color).pack(side="left")
        self.color_btn = tk.Label(cf, width=3, bg=self.rgb(self.color))
        self.color_btn.pack(side="left", padx=5)

        self.titulo(p, "Tamaño")
        tf = tk.Frame(p)
        tf.pack(fill="x")
        tk.Scale(tf, from_=1, to=500, orient="horizontal",
                 variable=self.tam,
                 command=lambda e: self.actualizar_preview()).pack(side="left", fill="x", expand=True)
        tk.Entry(tf, width=5, textvariable=self.tam).pack(side="right")

        self.titulo(p, "Fuente")
        tk.OptionMenu(p, self.fuente, *self.cargar_fuentes(),
                      command=lambda e: self.actualizar_preview()).pack(fill="x")

        self.titulo(p, "Posición")
        tk.OptionMenu(p, self.pos,
                      "Arriba Izquierda", "Arriba Derecha",
                      "Abajo Izquierda", "Abajo Derecha",
                      command=lambda e: self.actualizar_preview()).pack(fill="x")

        self.titulo(p, "Margen")
        tk.Checkbutton(p, text="Usar margen", variable=self.usar_margen,
                       command=self.actualizar_preview).pack(anchor="w")
        tk.Scale(p, from_=0, to=200, orient="horizontal",
                 variable=self.margen,
                 command=lambda e: self.actualizar_preview()).pack(fill="x")

        self.titulo(p, "Rendimiento")
        tk.Checkbutton(p, text="Modo Turbo (multiproceso)",
                       variable=self.modo_turbo).pack(anchor="w")

        self.titulo(p, "Presets")
        tk.Button(p, text="Guardar preset", command=self.guardar_preset).pack(fill="x")
        tk.Button(p, text="Cargar preset", command=self.cargar_preset).pack(fill="x")

        tk.Button(p, text="Aplicar a todas",
                  bg="#4CAF50", fg="white",
                  font=("Arial", 12, "bold"),
                  command=self.procesar).pack(pady=15, fill="x")

    def ui_preview(self):
        tk.Label(self.preview, text="Previsualización",
                 font=("Arial", 12, "bold")).pack()
        self.lbl = tk.Label(self.preview)
        self.lbl.pack(pady=5)

        nav = tk.Frame(self.preview)
        nav.pack()
        tk.Button(nav, text="◀", command=self.prev).pack(side="left")
        self.cont = tk.Label(nav)
        self.cont.pack(side="left", padx=10)
        tk.Button(nav, text="▶", command=self.next).pack(side="left")

    # ================= FUNCIONES =================

    def cargar_fuentes(self):
        return [f for f in os.listdir(FUENTES_DIR) if f.lower().endswith(".ttf")]

    def sel_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.archivos = [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(EXTS)]
            self.origen.set(d)
            self.idx = 0
            self.actualizar_preview()

    def sel_fotos(self):
        f = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.jpg *.png *.jpeg *.bmp *.tiff *.webp")])
        if f:
            self.archivos = list(f)
            self.origen.set(f"{len(f)} fotos")
            self.idx = 0
            self.actualizar_preview()

    def sel_destino(self):
        d = filedialog.askdirectory(title="Selecciona carpeta de destino")
        if d:
            self.destino.set(d)

    def elegir_color(self):
        c = colorchooser.askcolor()[0]
        if c:
            self.color = tuple(map(int, c))
            self.color_btn.config(bg=self.rgb(self.color))
            self.actualizar_preview()

    def aplicar_texto(self, img):
        draw = ImageDraw.Draw(img)
        fuente = ImageFont.truetype(os.path.join(FUENTES_DIR, self.fuente.get()), self.tam.get())
        texto = self.texto.get()

        w, h = img.size
        bbox = draw.textbbox((0, 0), texto, font=fuente)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        m = self.margen.get() if self.usar_margen.get() else 0

        pos = {
            "Arriba Izquierda": (m, m),
            "Arriba Derecha": (w-tw-m, m),
            "Abajo Izquierda": (m, h-th-m),
            "Abajo Derecha": (w-tw-m, h-th-m)
        }[self.pos.get()]

        draw.text(pos, texto, fill=self.color, font=fuente)
        return img

    def actualizar_preview(self):
        if not self.archivos:
            return
        try:
            img = Image.open(self.archivos[self.idx]).convert("RGB")
            img = self.aplicar_texto(img)
            img.thumbnail((420, 420))
            tkimg = ImageTk.PhotoImage(img)
            self.lbl.config(image=tkimg)
            self.lbl.image = tkimg
            self.cont.config(text=f"{self.idx+1} / {len(self.archivos)}")
        except:
            pass

    def prev(self):
        self.idx = (self.idx - 1) % len(self.archivos)
        self.actualizar_preview()

    def next(self):
        self.idx = (self.idx + 1) % len(self.archivos)
        self.actualizar_preview()

    # ================= PRESETS =================

    def guardar_preset(self):
        f = filedialog.asksaveasfilename(defaultextension=".json")
        if f:
            with open(f, "w") as fp:
                json.dump({
                    "texto": self.texto.get(),
                    "fuente": self.fuente.get(),
                    "tam": self.tam.get(),
                    "color": self.color,
                    "pos": self.pos.get(),
                    "margen": self.margen.get(),
                    "usar_margen": self.usar_margen.get()
                }, fp, indent=4)

    def cargar_preset(self):
        f = filedialog.askopenfilename(filetypes=[("Preset", "*.json")])
        if f:
            with open(f) as fp:
                p = json.load(fp)
            self.texto.set(p["texto"])
            self.fuente.set(p["fuente"])
            self.tam.set(p["tam"])
            self.color = tuple(p["color"])
            self.color_btn.config(bg=self.rgb(self.color))
            self.pos.set(p["pos"])
            self.margen.set(p["margen"])
            self.usar_margen.set(p["usar_margen"])
            self.actualizar_preview()

    # ================= PROCESO =================

    def procesar(self):
        if not self.archivos:
            messagebox.showwarning("Aviso", "No hay imágenes seleccionadas")
            return

        # Determinar carpeta de salida
        if self.destino.get():
            # Usar carpeta personalizada
            out = self.destino.get()
        elif len(self.archivos) > 1 and os.path.dirname(self.archivos[0]) == os.path.dirname(self.archivos[1]):
            # Todas en la misma carpeta, crear subcarpeta "fechadas"
            out = os.path.join(os.path.dirname(self.archivos[0]), "fechadas")
        else:
            # Diferentes carpetas, pedir destino
            out = filedialog.askdirectory(title="Selecciona carpeta de salida")
            if not out:
                return
        
        os.makedirs(out, exist_ok=True)

        # Crear ventana de progreso
        modal = tk.Toplevel(self.root)
        modal.title("Procesando")
        modal.geometry("500x200")
        modal.transient(self.root)
        modal.grab_set()
        
        ttk.Label(modal, text="Procesando imágenes...", font=("Arial", 11)).pack(pady=10)
        pb = ttk.Progressbar(modal, maximum=len(self.archivos), mode='determinate')
        pb.pack(fill="x", padx=20, pady=10)
        lbl = ttk.Label(modal, text="0 / 0")
        lbl.pack()
        lbl_archivo = ttk.Label(modal, text="", wraplength=450)
        lbl_archivo.pack(pady=5)

        # Variables de control
        resultados = []
        errores = []
        procesado = [0]
        terminado = [False]

        cfg = {
            "texto": self.texto.get(),
            "fuente": self.fuente.get(),
            "tam": self.tam.get(),
            "color": self.color,
            "pos": self.pos.get(),
            "margen": self.margen.get(),
            "usar_margen": self.usar_margen.get()
        }

        # Verificar configuración
        if not cfg["texto"]:
            modal.destroy()
            messagebox.showwarning("Aviso", "Debes escribir un texto")
            return

        def run():
            """Thread que ejecuta el procesamiento multiproceso"""
            try:
                if self.modo_turbo.get():
                    # Modo multiproceso
                    num_procesos = max(1, mp.cpu_count() - 1)
                    with mp.Pool(num_procesos) as pool:
                        for result in pool.imap_unordered(
                                worker_mp,
                                [(a, out, cfg) for a in self.archivos]):
                            resultados.append(result)
                else:
                    # Modo secuencial (más confiable para debugging)
                    for archivo in self.archivos:
                        result = worker_mp((archivo, out, cfg))
                        resultados.append(result)
            except Exception as e:
                import traceback
                resultados.append(("FATAL", "Error general", f"{str(e)}\n{traceback.format_exc()}"))
            finally:
                terminado[0] = True

        # Iniciar procesamiento
        threading.Thread(target=run, daemon=True).start()

        def poll():
            """Actualiza la UI con el progreso"""
            # Procesar resultados disponibles
            while procesado[0] < len(resultados):
                msg = resultados[procesado[0]]
                procesado[0] += 1
                
                if msg[0] == "OK":
                    pb["value"] = procesado[0]
                    lbl_archivo.config(text=f"✓ {os.path.basename(msg[1])}")
                elif msg[0] == "FATAL":
                    modal.destroy()
                    messagebox.showerror("Error Fatal", 
                        f"Error en el procesamiento:\n\n{msg[2]}\n\n"
                        f"Procesadas: {procesado[0]-1} de {len(self.archivos)}")
                    return
                else:  # ERR
                    errores.append(msg)
                    pb["value"] = procesado[0]
                    lbl_archivo.config(text=f"✗ {os.path.basename(msg[1])}")
                
                lbl.config(text=f"{procesado[0]} / {len(self.archivos)}")
                modal.update()

            # Verificar si terminó
            if terminado[0] and procesado[0] >= len(self.archivos):
                modal.destroy()
                
                exitos = procesado[0] - len(errores)
                msg_txt = f"Proceso terminado\n\nProcesadas correctamente: {exitos} de {len(self.archivos)}"
                msg_txt += f"\n\nCarpeta de salida:\n{out}"
                
                if errores:
                    log_file = os.path.join(out, "errores_fechador.txt")
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write(f"REPORTE DE ERRORES - Fechador de Fotos\n")
                        f.write(f"="*60 + "\n\n")
                        f.write(f"Total de imágenes: {len(self.archivos)}\n")
                        f.write(f"Procesadas correctamente: {exitos}\n")
                        f.write(f"Con errores: {len(errores)}\n\n")
                        f.write(f"="*60 + "\n\n")
                        for i, e in enumerate(errores, 1):
                            f.write(f"ERROR {i}:\n")
                            f.write(f"Archivo: {e[1]}\n")
                            f.write(f"Detalle: {e[2]}\n")
                            f.write("-"*60 + "\n\n")
                    msg_txt += f"\n\n⚠ Errores: {len(errores)}\nVer: errores_fechador.txt"
                    messagebox.showwarning("Proceso completado con errores", msg_txt)
                else:
                    messagebox.showinfo("¡Éxito!", msg_txt)
                return
            
            # Continuar polling
            self.root.after(50, poll)

        poll()

    def rgb(self, c):
        return "#%02x%02x%02x" % c


# ================= RUN =================

if __name__ == "__main__":
    mp.freeze_support()
    root = tk.Tk()
    FechadorApp(root)
    root.mainloop()
