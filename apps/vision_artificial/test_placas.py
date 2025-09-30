import requests

# Guarda esto como test_plate_api.py
url = "https://api.platerecognizer.com/v1/plate-reader/"
headers = {"Authorization": "Token 3bfcad5ee8d854fe155db1ec3e3fe64f252e763c"}

# Prueba con URL de imagen
data = {"upload": "https://res.cloudinary.com/dlhfdfu6l/image/upload/v1735567300/fotoReferenciaCondominium/tu_imagen_aqui.jpg"}

response = requests.post(url, data=data, headers=headers)
print("Status:", response.status_code)
print("Response:", response.json())