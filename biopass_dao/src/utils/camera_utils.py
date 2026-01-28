import cv2
import numpy as np

class CameraUtils:

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    @classmethod
    def detectar_rostro(cls, frame):
        """ Detecta y recorta la cara. """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cls.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0: return None, None
        
        (x, y, w, h) = faces[0]

        return gray[y:y+h, x:x+w], (x, y, w, h)

    @staticmethod
    def convertir_a_bytes(img):
        """ Convierte imagen OpenCV a Bytes para la BD """
        return cv2.imencode('.jpg', img)[1].tobytes()

    @staticmethod
    def bytes_a_imagen(data):
        """ Convierte Bytes de la BD a imagen OpenCV """
        return cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)

    @classmethod
    def entrenar_y_predecir(cls, lista_usuarios, rostro_actual):
        """ Entrenamiento Lazy: Entrena al momento con los datos de la BD """
        faces, ids, names = [], [], {}

        for user in lista_usuarios:
            img = cls.bytes_a_imagen(user['foto_bytes'])
            if img is not None:
                faces.append(img)
                ids.append(user['id'])
                names[user['id']] = user['nombre']

        if not faces: return "Desconocido"

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(ids))

        id_pred, conf = recognizer.predict(rostro_actual)

        if conf < 80:
            return names.get(id_pred, "Desconocido")
        return "Desconocido"