# Importaciones
import json
import boto3

iot_client = boto3.client('iot-data')

# Estructura principal de la función lambda
def lambda_handler(event, context):
    print("Evento recibido:", json.dumps(event, indent=2))

    # Session attributes base
    session_attributes = event.get('session', {}).get('attributes', {})

    request_type = event['request']['type']

    if request_type == 'LaunchRequest':
        return build_response ("Robot iniciado", session_attributes, False)

    elif request_type == 'SessionEndedRequest':
        print(f"Sesión terminada por razón: {event['request']['reason']}")
        return build_response("", session_attributes, True)
        
    elif request_type == 'IntentRequest':
        intent_name = event['request']['intent']['name']
        print(f"Intent: {intent_name}")

        if intent_name == 'MoveRobotIntent':
            command = event['request']['intent']['slots']['direction'].get('resolutions',{})
            try:
                if command == {}:
                    command = event['request']['intent']['slots']['instruction']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
                else:
                    command = event['request']['intent']['slots']['direction']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
            except (KeyError, AttributeError) as e:
                print(f"Error getting command: {str(e)}")
                return build_response("No se ha podido determinar la dirección del movimiento", session_attributes, False)

            # Diccionario de comandos
            command_mapping = {
                'adelante': 'A',
                'atras': 'R',
                'izquierda': 'I',
                'derecha': 'D',
                'detener': 'P'
            }

            # Diccionario de respuestas
            response_command_mapping = {
                'adelante': 'Avanzando',
                'atras': 'Retrocediendo',
                'izquierda': 'Caminando hacia la izquierda',
                'derecha': 'Caminando hacia la derecha',
                'detener': 'Deteniendo'
            }

            # Normalizar el comando y obtener el código MQTT
            normalized_command = command.lower().strip()
            response_text = response_command_mapping.get(normalized_command, "Comando no reconocido")
            mqtt_command = command_mapping.get(normalized_command, "P") # Usamos P como opción predeterminada por protección

            # Envío de mensaje
            response = iot_client.publish(
                topic='robot/control',
                qos=1,
                payload=mqtt_command
            )

            return build_response(response_text, session_attributes, False)
           
        elif intent_name == 'ResourceRobotIntent':
            return handle_video_intent(event, session_attributes)

        elif intent_name in ["AMAZON.StopIntent", "AMAZON.CancelIntent"]:
            # Publicar comando de parada antes de cerrar
            iot_client.publish(
                topic='robot/control',
                qos=1,
                payload="P"
            )
            return build_response("Deteniendo el robot, ¡Hasta luego!", session_attributes, True)
            
        elif intent_name == 'AMAZON.HelpIntent':
            return build_response("Puedes decirme que quieres que haga el robot, por ejemplo, adelante, atras, izquierda, derecha o detener", session_attributes, False)

        elif intent_name == "AMAZON.ResumeIntent":
            return build_response("Resume Intent aún no está funcionando", session_attributes, False)
        
        elif intent_name == "AMAZON.PauseIntent":
            return build_response("Pause Intent aún no está funcionando", session_attributes, False)

        else:
            return build_response("Intent no reconocido", session_attributes, False)
    
    # Respuesta por defecto para intents no reconocidos
    return build_response('No entendí el comando. ¿Puedes repetirlo?', session_attributes, False)
            
    def error_response(message):
        return {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': f'{message} no es valido, intentelo de nuevo'
                },
                'shouldEndSession': False
            }
        }

def build_response(speech_text, session_attributes, should_end_session):
    # Construye una respuesta básica sin video
    response = {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech_text
            },
            'shouldEndSession': should_end_session
        }
    }

    # Solo incluir directives si estamos en una respuesta de video
    if "video" in speech_text.lower() and "reproduciendo" in speech_text.lower():
        # Esto lo manejamos en handle_video_intent
        pass
        
    return response

def handle_video_intent(event, session_attributes):   
    # Maneja específicamente el intent de video
    try:
        # Verificar capacidades del dispositivo
        supported_interfaces = event.get('context', {}).get('System', {}).get('device', {}).get('supportedInterfaces', {})
        print("Interfaces soportadas:", json.dumps(supported_interfaces, indent=2))
        
        if 'VideoApp' not in supported_interfaces:
            print("El dispositivo no soporta video")
            return build_response("Este dispositivo no soporta video", session_attributes, False)
        
        # URL de video que SÍ funciona con Alexa
        video_url = "https://d2zihajmogu5jn.cloudfront.net/bipbop-advanced/bipbop_16x9_variant.m3u8"
        
        # Alternativas de prueba:
        # video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
        # video_url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        
        # Construir respuesta con video
        response = {
            'version': '1.0',
            'sessionAttributes': session_attributes,
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'Reproduciendo video del robot'
                },
                'directives': [
                    {
                        'type': 'VideoApp.Launch',
                        'videoItem': {
                            'source': video_url,
                            'metadata': {
                                'title': 'Cámara Robot',
                                'subtitle': 'Transmisión en vivo'
                            }
                        }
                    }
                ]
            }
        }
        
        print("Respuesta con video:", json.dumps(response, indent=2))
        return response
        
    except Exception as e:
        print(f"Error en handle_video_intent: {str(e)}")
        return build_response(f"Error al reproducir video: {str(e)}", session_attributes, False)
