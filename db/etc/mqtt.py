import requests
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화
cred = credentials.Certificate("C:/Users/User/Desktop/db/raspteam33-firebase-adminsdk-maygo-0399ab2f21.json")  # Firebase 인증 키
firebase_admin.initialize_app(cred)
db = firestore.client()

# Homebridge IP, 포트 및 장치 정보 설정
homebridge_ip = "172.20.10.2"
homebridge_port = 8581
aircon_id = "fadca004ce402eede2f2e76b1384a032ccb19d2e8ce87fcc5a196a69a014bd8f"
plug_id = "70c9fc40cde74506b38dc35a71911c25351c115e86c9f622098bf06297986aed"
aircon_state = 0
plug_state = 0

# 초기 토큰 가져오기
token = None
def get_token():
    url = f"http://{homebridge_ip}:{homebridge_port}/api/auth/login"
    payload = {
        "username": "pwh1219",
        "password": "1219"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if response.status_code == 201:
        print("Token refreshed successfully.")
        return data.get("access_token")
    else:
        print(f"Failed to refresh token: {data}")
        return None

# 초기 토큰 설정
token = get_token()

# Firestore 상태 업데이트 함수
def update_firestore_state(device_name, state):
    """
    Firestore의 state 필드를 업데이트합니다.
    :param device_name: 장치명 (예: "aircon", "plug")
    :param state: 장치 상태 ("on" 또는 "off")
    """
    devices_ref = db.collection('Stores').document('store1').collection('Devices')
    
    # 필드 이름 백틱으로 묶기
    query = devices_ref.where('`장치명`', '==', device_name).stream()

    for doc in query:
        doc_id = doc.id
        devices_ref.document(doc_id).update({"state": state})
        print(f"Updated Firestore: {device_name} -> {state}")


# Aircon 제어 함수
def control_aircon(characteristic_type, value):
    global token
    url = f"http://{homebridge_ip}:{homebridge_port}/api/accessories/{aircon_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    control = {
        "characteristicType": characteristic_type,
        "value": value
    }

    try:
        response = requests.put(url, headers=headers, json=control)
        if response.status_code == 401:  # 토큰 만료 시 토큰 갱신
            print("Token expired. Refreshing token...")
            token = get_token()
            if token:  # 토큰 갱신 성공 시 재요청
                headers["Authorization"] = f"Bearer {token}"
                response = requests.put(url, headers=headers, json=control)
        print(f"Aircon Control Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while controlling aircon: {e}")

# Plug 제어 함수
def control_plug(characteristic_type, value):
    global token
    url = f"http://{homebridge_ip}:{homebridge_port}/api/accessories/{plug_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    control = {
        "characteristicType": characteristic_type,
        "value": value
    }

    try:
        response = requests.put(url, headers=headers, json=control)
        if response.status_code == 401:  # 토큰 만료 시 토큰 갱신
            print("Token expired. Refreshing token...")
            token = get_token()
            if token:  # 토큰 갱신 성공 시 재요청
                headers["Authorization"] = f"Bearer {token}"
                response = requests.put(url, headers=headers, json=control)
        print(f"Plug Control Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while controlling plug: {e}")

# MQTT 메시지 처리 함수
def on_message(client, userdata, message):
    global aircon_state, plug_state
    device_name = message.payload.decode()
    print(f"Received MQTT message: {device_name}")

    if device_name == "aircon":
        aircon_state = 1 - aircon_state
        control_aircon("Active", aircon_state)
        update_firestore_state("aircon", "on" if aircon_state == 1 else "off")
    elif device_name == "plug":
        plug_state = 1 - plug_state
        control_plug("On", plug_state)
        update_firestore_state("plug", "on" if plug_state == 1 else "off")

# MQTT 설정
mqtt_broker = "broker.hivemq.com"
mqtt_port = 1883
mqtt_topic = "ESTeam3/control"

# MQTT 클라이언트 설정
client = mqtt.Client()
client.on_message = on_message

# MQTT 브로커 연결
client.connect(mqtt_broker, mqtt_port, 60)

# MQTT 구독 시작
client.subscribe(mqtt_topic)

# MQTT 루프 실행
if __name__ == "__main__":
    try:
        print("Starting MQTT client...")
        client.loop_forever()
    except KeyboardInterrupt:
        print("MQTT client stopped.")
