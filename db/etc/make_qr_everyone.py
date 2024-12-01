import qrcode
import base64
from firebase_admin import credentials, firestore, initialize_app
import os

# Firebase Admin SDK 초기화
cred = credentials.Certificate("C:/Users/User/Desktop/db/raspteam33-firebase-adminsdk-maygo-0399ab2f21.json")
initialize_app(cred)
db = firestore.client()

# Firestore에서 worker ID 가져오기
workers_ref = db.collection("Stores").document("store1").collection("Workers")
docs = workers_ref.stream()

# QR 코드 생성 및 Firestore에 저장
output_folder = "qrcodes"  # QR 코드 임시 저장 폴더
os.makedirs(output_folder, exist_ok=True)

for doc in docs:
    worker_id = doc.id  # Firestore의 worker 고유 ID
    qr_data = worker_id  # QR 코드 데이터에 worker_id만 포함
    qr = qrcode.make(qr_data)  # QR 코드 생성

    # 로컬에 QR 코드 이미지 저장
    qr_filename = os.path.join(output_folder, f"{worker_id}.png")
    qr.save(qr_filename)
    print(f"QR 코드 생성 완료: {qr_filename}")

    # 이미지 파일을 Base64로 인코딩
    with open(qr_filename, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read()).decode('utf-8')

    # Firestore에 Base64 문자열 저장
    workers_ref.document(worker_id).update({
        "qr_img_base64": base64_encoded  # Firestore에 Base64 데이터 저장
    })
    print(f"Firestore에 Base64 이미지 저장 완료: worker_id={worker_id}")
