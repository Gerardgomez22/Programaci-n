import tkinter as tk
from tkinter import messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import os

from src.usuario_dao import UsuarioDAO
from src.utils.camera_utils import CameraUtils

print("--- EL PROGRAMA ESTÁ INTENTANDO ARRANCAR ---")

class BioPassApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BioPass DAO - Sistema de Acceso")
        self.root.geometry("800x600")

        self.cap = cv2.VideoCapture(0)

        self.video_label = tk.Label(self.root)
        self.video_label.pack(pady=20)

        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(pady=20)

        self.btn_registro = tk.Button(self.btn_frame, text="Registrar Nuevo Usuario", command=self.registrar_usuario, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.btn_registro.pack(side=tk.LEFT, padx=20)

        self.btn_login = tk.Button(self.btn_frame, text="Iniciar Sesión (Login)", command=self.login_usuario, bg="#2196F3", fg="white", font=("Arial", 12))
        self.btn_login.pack(side=tk.LEFT, padx=20)

        self.rostro_detectado = None
        self.frame_actual = None

        self.mostrar_video()

    def mostrar_video(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame_actual = frame
            
            # Detectar rostro
            rostro, coords = CameraUtils.detectar_rostro(frame)

            if coords is not None:
                (x, y, w, h) = coords
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                self.rostro_detectado = rostro
            else:
                self.rostro_detectado = None

            # Pintar en Tkinter
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(10, self.mostrar_video)

    def registrar_usuario(self):
        """
        Lógica corregida para evitar el error cv2.error: !_img.empty()
        """
        if self.rostro_detectado is None:
            messagebox.showwarning("Cuidado", "No detecto ningún rostro. Ponte frente a la cámara.")
            return

        # --- CORRECCIÓN IMPORTANTE ---
        # Hacemos una copia de la cara AHORA MISMO.
        # Esto congela la imagen en memoria antes de abrir la ventana del nombre.
        cara_congelada = self.rostro_detectado.copy()
        # -----------------------------

        nombre = simpledialog.askstring("Registro", "Introduce tu nombre:")
        if not nombre:
            return

        # Usamos 'cara_congelada' en vez de 'self.rostro_detectado'
        # porque 'self.rostro_detectado' puede haberse borrado mientras escribías.
        foto_bytes = CameraUtils.convertir_a_bytes(cara_congelada)
        
        if foto_bytes:
            exito = UsuarioDAO.registrar_usuario(nombre, foto_bytes)
            
            if exito:
                messagebox.showinfo("Éxito", f"Usuario {nombre} guardado correctamente en la BD.")
            else:
                messagebox.showerror("Error", "Falló la conexión o el registro.")

    def login_usuario(self):
        if self.rostro_detectado is None:
            messagebox.showwarning("Cuidado", "No veo tu cara.")
            return

        print("Descargando usuarios de la BD...")
        lista_usuarios = UsuarioDAO.obtener_todos()
        
        if not lista_usuarios:
            messagebox.showerror("Error", "La base de datos está vacía o no hay conexión.")
            return

        # Aquí usamos la cara en vivo porque es instantáneo (no hay ventana de escribir)
        resultado = CameraUtils.entrenar_y_predecir(lista_usuarios, self.rostro_detectado)

        if resultado != "Desconocido":
            messagebox.showinfo("Bienvenido", f"¡Hola de nuevo, {resultado}!")
        else:
            messagebox.showerror("Acceso Denegado", "No te reconozco. ¿Estás registrado?")

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BioPassApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()