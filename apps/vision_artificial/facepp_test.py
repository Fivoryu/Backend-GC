import requests
from decouple import config

def comparar_caras_facepp(url_foto1, url_foto2):
    api_key = config('FACEPP_API_KEY')
    api_secret = config('FACEPP_API_SECRET')
    url = "https://api-us.faceplusplus.com/facepp/v3/compare"

    data = {
        "api_key": api_key,
        "api_secret": api_secret,
        "image_url1": url_foto1,
        "image_url2": url_foto2
    }

    resp = requests.post(url, data=data)
    return resp.json()

# Prueba con dos URLs de fotos (pueden ser de Cloudinary)
resultado = comparar_caras_facepp(
    "https://res.cloudinary.com/dlhfdfu6l/image/upload/v1759005171/fotoReferenciaCondominium/Henry_Cavilljpg_emeqow.jpg",
    "https://res.cloudinary.com/dlhfdfu6l/image/upload/v1758986698/fotoReferenciaCondominium/HenryCavill_ozo1ip.jpg"
)

print(resultado)