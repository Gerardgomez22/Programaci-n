import cv2
import numpy as np
import os

class CameraUtils:
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    @classmethod
    def detectar_rostro(cls, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cls.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None, None
        (x, y, w, h) = faces[0]
        rostro = gray[y:y+h, x:x+w]

        return rostro, (x, y, w, h)

    @staticmethod
    def convertir_a_bytes(imagen_cv2):

        exito, buffer = cv2.imencode('.jpg', imagen_cv2)
        if exito:
            return buffer.tobytes()
        return None

    @staticmethod
    def bytes_a_imagen(datos_bytes):

        nparr = np.frombuffer(datos_bytes, np.uint8)

        return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    @classmethod
    def entrenar_y_predecir(cls, lista_usuarios, rostro_incognita):

        if not lista_usuarios:
            return "Desconocido"

        rostros_entrenamiento = []
        etiquetas = []

        mapa_nombres = {}

        print("--> Iniciando entrenamiento en RAM...")
        
        for usuario in lista_usuarios:

            try:

                imagen_recuperada = cls.bytes_a_imagen(usuario['foto_bytes'])
                
                if imagen_recuperada is not None:

                    rostros_entrenamiento.append(imagen_recuperada)
                    etiquetas.append(usuario['id'])
                    mapa_nombres[usuario['id']] = usuario['nombre']
            except Exception as e:
                print(f"Error procesando usuario {usuario['id']}: {e}")
                continue

        if not rostros_entrenamiento:
            return "Error: No hay datos para entrenar"

        recognizer = cv2.face.LBPHFaceRecognizer_create()

        recognizer.train(rostros_entrenamiento, np.array(etiquetas))

        id_predicho, confianza = recognizer.predict(rostro_incognita)

        if confianza < 85:
            nombre = mapa_nombres.get(id_predicho, "Desconocido")
            return f"{nombre} ({confianza:.1f})"
        else:
            return "Desconocido"