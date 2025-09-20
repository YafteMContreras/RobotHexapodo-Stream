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
            try:
                command = event['request']['intent']['slots']['direction']['value']
            except (KeyError, AttributeError) as e:
                print(f"Error getting command: {str(e)}")
                return {
                    'version': '1.0',
                    'response': {
                        'outputSpeech': {
                            'type': 'PlainText',
                            'text': 'No se ha podido determinar la direccion del movimiento'
                        }
                    }
                }

            # Diccionario de comandos
            command_mapping = {
                'adelante': 'A',
                'atrás': 'R',
                'avanza': 'A',
                'retrocede': 'R',
                'izquierda': 'I',
                'derecha': 'D',
                'detener': 'P',
                'camara': 'C',
                'video': 'C'
            }

            # Diccionario de respuestas
            command_mapping_response = {
                'adelante': 'A',
                'atrás': 'R',
                'avanza': 'A',
                'retrocede': 'R',
                'izquierda': 'I',
                'derecha': 'D',
                'detener': 'P',
                'camara': 'C',
                'video': 'C'
            }

            # Normalizar el comando y obtener el código MQTT
            normalized_command = command.lower().strip()
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
                        'text': f'Ejecutando comando {command}'
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