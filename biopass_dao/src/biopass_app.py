import tkinter as tk
from tkinter import messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
from src.usuario_dao import UsuarioDAO
from src.utils.camera_utils import CameraUtils

class BioPassApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BioPass DAO")
        self.root.geometry("800x600")

        self.cap = cv2.VideoCapture(0)
        self.rostro_detectado = None

        self.video_label = tk.Label(self.root)
        self.video_label.pack(pady=20)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Registrar", command=self.registrar, bg="green", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Entrar (Login)", command=self.login, bg="blue", fg="white").pack(side=tk.LEFT, padx=10)

        self.mostrar_video()

    def mostrar_video(self):
        ret, frame = self.cap.read()
        if ret:
            rostro, _ = CameraUtils.detectar_rostro(frame)
            self.rostro_detectado = rostro 

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(10, self.mostrar_video)

    def registrar(self):
        if self.rostro_detectado is None:
            messagebox.showwarning("Aviso", "No se detecta rostro.")
            return

        nombre = simpledialog.askstring("Registro", "Nombre:")
        if not nombre: return

        bytes_foto = CameraUtils.convertir_a_bytes(self.rostro_detectado.copy())
        
        if UsuarioDAO.registrar_usuario(nombre, bytes_foto):
            messagebox.showinfo("Éxito", "Usuario guardado.")
        else:
            messagebox.showerror("Error", "Error al guardar en BD.")

    def login(self):
        if self.rostro_detectado is None:
            messagebox.showwarning("Aviso", "No se detecta rostro.")
            return

        usuarios = UsuarioDAO.obtener_todos()
        if not usuarios:
            messagebox.showerror("Error", "Base de datos vacía.")
            return

        nombre = CameraUtils.entrenar_y_predecir(usuarios, self.rostro_detectado)
        
        if nombre != "Desconocido":
            messagebox.showinfo("Bienvenido", f"Hola, {nombre}")
        else:
            messagebox.showerror("Acceso Denegado", "No reconocido.")

    def on_closing(self):
        if self.cap.isOpened(): self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BioPassApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()