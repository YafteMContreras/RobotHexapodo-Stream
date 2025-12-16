import requests
import boto3
from datetime import datetime

def obtener_ngrok_url():
    try:
        data = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        for t in data["tunnels"]:
            if t["proto"] == "https":
                return t["public_url"]
        return None
    except Exception as e:
        print("Error:", e)
        return None

# Crear cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table("LinkVideoRobotHexapodo")

def actualizar_estado(url):
    response = tabla.update_item(
        Key={"robotID": "hexapod_prueba"},
        UpdateExpression="SET videoUrl = :v",
        ExpressionAttributeValues={":v": url}
    )
    print("Item actualizado:", response)

actualizar_estado(obtener_ngrok_url())
