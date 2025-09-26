# Importaciones
import json
import boto3

iot_client = boto3.client('iot-data')

# Estructura principal de la función lambda
def lambda_handler(event, context):
    request_type = event['request']['type']

    if request_type == 'LaunchRequest':
        return {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'Robot iniciado'
                },
                'shouldEndSession': False
            }
        }

    elif request_type == 'SessionEndedRequest':
        print(f"Sesión terminada por razón: {event['request']['reason']}")
        return {
            'version': '1.0',
            'response': {
                'shouldEndSession': True
            }
        }

    elif request_type == 'IntentRequest':
        intent_name = event['request']['intent']['name']

        if intent_name == 'MoveRobotIntent':
            command = event['request']['intent']['slots']['direction'].get('resolutions',{})
            try:
                if command == {}:
                    command = event['request']['intent']['slots']['instruction']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
                else:
                    command = event['request']['intent']['slots']['direction']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
            except (KeyError, AttributeError) as e:
                print(f"Error getting command: {str(e)}")
                return {
                    'version': '1.0',
                    'response': {
                        'outputSpeech': {
                            'type': 'PlainText',
                            'text': 'No se ha podido determinar la dirección del movimiento'
                        }
                    }
                }

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

            return {
                'version': '1.0',
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': f'{response_text}'
                    },
                    'shouldEndSession': False
                }
            }
        elif intent_name == 'ResourceRobotIntent':
            # Verificar si el dispositivo tiene capacidad de video
            supported_interfaces = event.get('context', {}).get('System', {}).get('device', {}).get('supportedInterfaces', {})

            if 'VideoApp' in supported_interfaces:
                # Dispositivo con pantalla - mostrar video
                try:
                    return {
                        'version': '1.0',
                        "sessionAttributes": {},  # aunque esté vacío
                        'response': {
                            'outputSpeech': {
                                'type': 'PlainText',
                                'text': 'Mostrando video'
                            },
                            "directives": [
                                {
                                    "type": "VideoApp.Launch",
                                    "videoItem": {
                                        "source": "https://drive.google.com/file/d/1il1yUQ7mxAhn0N7czTLox5yeymp0TV1I/view?usp=sharing"
                                    }
                                }
                            ],
                            'shouldEndSession': True
                        }
                    }
                
                except Exception as e:
                    print(f"Error getting command: {str(e)}")
                    return {
                        'version': '1.0',
                        'response': {
                            'outputSpeech': {
                                'type': 'PlainText',
                                'text': 'Se ha producido un error al mostrar el video'
                            }
                        }
                    }

            else:
                # Dispositivo sin pantalla - mostrar mensaje de error
                return {
                    'version': '1.0',
                    'response': {
                        'outputSpeech': {
                            'type': 'PlainText',
                            'text': 'Lo siento, este dispositivo no tiene pantalla para mostrar el video'
                        },
                        'shouldEndSession': False
                    }
                }


        elif intent_name in ["AMAZON.StopIntent", "AMAZON.CancelIntent"]:
            # Publicar comando de parada antes de cerrar
            iot_client.publish(
                topic='robot/control',
                qos=1,
                payload="P"
            )

            return {
                'version': '1.0',
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': 'Deteniendo el robot, ¡Hasta luego!'
                    },
                    'shouldEndSession': True
                }
            }

        elif intent_name == 'AMAZON.HelpIntent':
            return{
                'version': '1.0',
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': 'Puedes decirme que quieres que haga el robot, por ejemplo, adelante, atras, izquierda, derecha o detener'
                    },
                    'shouldEndSession': False
                }
                
            }

        elif intent_name == "AMAZON.ResumeIntent":
            return{
                'version': '1.0',
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': 'Resume Intent aún no está funcionando'
                    },
                    'shouldEndSession': False
                }
            }
        
        elif intent_name == "AMAZON.PauseIntent":
            return{
                'version': '1.0',
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': 'Pause Intent aún no está funcionando'
                    },
                    'shouldEndSession': False
                }
            }

        else:
            return {
                'version': '1.0',
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': 'Lo siento, no entiendo lo que me has dicho'
                    },
                    'shouldEndSession': False
                }
            }
    
    # Respuesta por defecto para intents no reconocidos
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': 'No entendí el comando. ¿Puedes repetirlo?'
            },
            'shouldEndSession': False
        }
    }
            
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