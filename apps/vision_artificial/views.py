from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from apps.residentes.models import Residente, Vehiculo
from .models import logReconocimiento, logReconocimientoPlaca
from .serializers import LogReconocimientoSerializer, LogReconocimientoPlacaSerializer
from decouple import config
import requests
import io


class ReconocimientoFacialView(APIView):
    def post(self, request):
        try:
            url_foto = request.data.get('foto_url')
            if not url_foto:
                return Response({'error': 'No se envió la foto'}, status=status.HTTP_400_BAD_REQUEST)
            
            residentes = Residente.objects.all()
            mejor_coincidencia = 0
            residente_encontrado = None
            confianza_umbral = 70

            for residente in residentes:
                try:
                    url_foto_residente = getattr(residente, 'foto_perfil', None)
                    if not url_foto_residente:
                        continue

                    api_key = config('FACEPP_API_KEY')
                    api_secret = config('FACEPP_API_SECRET')
                    url = "https://api-us.faceplusplus.com/facepp/v3/compare"
                    data = {
                        "api_key": api_key,
                        "api_secret": api_secret,
                        "image_url1": url_foto,
                        "image_url2": url_foto_residente
                    }
                    resp = requests.post(url, data=data)
                    result = resp.json()
                    confidence = result.get('confidence', 0)
                    if confidence > mejor_coincidencia:
                        mejor_coincidencia = confidence
                        residente_encontrado = residente
                    if mejor_coincidencia >= confianza_umbral:
                        break
                except Exception as e:
                    continue

            try:
                if residente_encontrado and mejor_coincidencia >= confianza_umbral:
                    log = logReconocimiento.objects.create(
                        residente=residente_encontrado,
                        foto_ruta=url_foto,
                        descripcion="Reconocimiento facial exitoso",
                        coincidencia=float(mejor_coincidencia)
                    )
                    return Response({
                        'autorizado': True,
                        'residente': {
                            'id': residente_encontrado.id,
                            'nombre': getattr(residente_encontrado, 'nombre', '') or '',
                            'apellido': getattr(residente_encontrado, 'apellidos', '') or '',
                            'foto_perfil': getattr(residente_encontrado, 'foto_perfil', '') or '',
                        },
                        'coincidencia': float(mejor_coincidencia)
                    }, status=status.HTTP_200_OK)
                else:
                    log = logReconocimiento.objects.create(
                        residente=None,
                        foto_ruta=url_foto,
                        descripcion="No pertenece al residencial",
                        coincidencia=float(mejor_coincidencia)
                    )
                    return Response({
                        'autorizado': False,
                        'mensaje': 'No se encontró coincidencia suficiente',
                        'coincidencia': float(mejor_coincidencia)
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': f'Error al guardar log: {str(e)}',
                    'autorizado': False,
                    'coincidencia': float(mejor_coincidencia)
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': f'Error interno del servidor: {str(e)}',
                'autorizado': False,
                'coincidencia': 0.0
            }, status=status.HTTP_200_OK)

class ReconocimientoPlacaView(APIView):
    def post(self, request):
        try:
            url_foto = request.data.get('foto_url')
            if not url_foto:
                return Response({'error': 'No se envió la foto'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Descargar la imagen de Cloudinary
            image_response = requests.get(url_foto)
            if image_response.status_code != 200:
                return Response({
                    'autorizado': False,
                    'mensaje': 'Error al descargar la imagen',
                    'confianza': 0.0
                }, status=status.HTTP_200_OK)

            # Preparar el archivo para la API de Plate Recognizer
            api_token = "3bfcad5ee8d854fe155db1ec3e3fe64f252e763c"
            headers = {'Authorization': f'Token {api_token}'}
            
            # Enviar como archivo binario
            files = {'upload': ('image.jpg', io.BytesIO(image_response.content), 'image/jpeg')}

            response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                files=files,
                headers=headers,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                print(f"Error API status: {response.status_code}, Response: {response.text}")
                return Response({
                    'autorizado': False,
                    'mensaje': f'Error en API de reconocimiento: {response.status_code}',
                    'confianza': 0.0
                }, status=status.HTTP_200_OK)

            result = response.json()
            print(f"API Response: {result}")
            
            if 'results' not in result or not result['results']:
                log = logReconocimientoPlaca.objects.create(
                    vehiculo=None,
                    foto_ruta=url_foto,
                    placa_detectada="",
                    descripcion="No se detectó ninguna placa",
                    confianza=0.0
                )
                return Response({
                    'autorizado': False,
                    'mensaje': 'No se detectó ninguna placa en la imagen',
                    'confianza': 0.0
                }, status=status.HTTP_200_OK)
            
            # Obtener el mejor resultado
            mejor_resultado = max(result['results'], key=lambda x: x.get('score', 0))
            placa_detectada = mejor_resultado['plate'].upper().strip()
            confianza = mejor_resultado.get('score', 0) * 100
            
            print(f"Placa detectada: '{placa_detectada}' con confianza: {confianza}%")
            
            # Buscar vehículo
            vehiculo_encontrado = None
            try:
                vehiculo_encontrado = Vehiculo.objects.filter(matricula__iexact=placa_detectada).first()
                print(f"Vehículo encontrado: {vehiculo_encontrado}")
            except Exception as e:
                print(f"Error en búsqueda: {e}")
            
            # Crear log y responder
            try:
                if vehiculo_encontrado:
                    log = logReconocimientoPlaca.objects.create(
                        vehiculo=vehiculo_encontrado,
                        foto_ruta=url_foto,
                        placa_detectada=placa_detectada,
                        descripcion="Placa reconocida - Vehículo autorizado",
                        confianza=float(confianza)
                    )
                    return Response({
                        'autorizado': True,
                        'vehiculo': {
                            'id': vehiculo_encontrado.id,
                            'matricula': vehiculo_encontrado.matricula,
                            'marca': vehiculo_encontrado.marca or '',
                            'modelo': vehiculo_encontrado.modelo or '',
                            'propietario': {
                                'nombre': vehiculo_encontrado.residente.nombre or '',
                                'apellido': vehiculo_encontrado.residente.apellidos or '',
                            }
                        },
                        'placa_detectada': placa_detectada,
                        'confianza': float(confianza)
                    }, status=status.HTTP_200_OK)
                else:
                    log = logReconocimientoPlaca.objects.create(
                        vehiculo=None,
                        foto_ruta=url_foto,
                        placa_detectada=placa_detectada,
                        descripcion="Placa no autorizada - No pertenece al residencial",
                        confianza=float(confianza)
                    )
                    return Response({
                        'autorizado': False,
                        'mensaje': 'Placa no autorizada - No pertenece al residencial',
                        'placa_detectada': placa_detectada,
                        'confianza': float(confianza)
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': f'Error al guardar log: {str(e)}',
                    'autorizado': False,
                    'confianza': float(confianza) if 'confianza' in locals() else 0.0
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"Error general: {e}")
            return Response({
                'error': f'Error interno del servidor: {str(e)}',
                'autorizado': False,
                'confianza': 0.0
            }, status=status.HTTP_200_OK)

class LogReconocimientoListView(generics.ListAPIView):
    serializer_class = LogReconocimientoSerializer
    
    def get_queryset(self):
        try:
            return logReconocimiento.objects.all().order_by('-fecha_hora')
        except Exception as e:
            return logReconocimiento.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response([], status=status.HTTP_200_OK)

class LogReconocimientoPlacaListView(generics.ListAPIView):
    serializer_class = LogReconocimientoPlacaSerializer
    
    def get_queryset(self):
        try:
            return logReconocimientoPlaca.objects.all().order_by('-fecha_hora')
        except Exception as e:
            return logReconocimientoPlaca.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response([], status=status.HTTP_200_OK)
