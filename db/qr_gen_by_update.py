import qrcode
import base64
from firebase_admin import credentials, firestore, initialize_app
import os

# Firebase Admin SDK 초기화
cred = credentials.Certificate("C:/Users/User/Desktop/db/raspteam333-firebase-adminsdk-rt6q8-a89d9b9278.json")
initialize_app(cred)
db = firestore.client()

# Firestore 리스너 등록
workers_ref = db.collection("workers")

# QR 코드 임시 저장 폴더
output_folder = "qrcodes"
os.makedirs(output_folder, exist_ok=True)

# Firestore 리스너 함수 정의
def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == "ADDED":  # 새로운 문서가 추가되었을 때
            worker_id = change.document.id  # 새로 추가된 worker ID
            print(f"새로운 worker 추가: {worker_id}")

            # QR 코드 생성
            qr_data = worker_id  # QR 코드 데이터에 worker_id만 포함
            qr = qrcode.make(qr_data)

            # 로컬에 QR 코드 이미지 저장
            qr_filename = os.path.join(output_folder, f"{worker_id}.png")
            qr.save(qr_filename)
            print(f"QR 코드 생성 완료: {qr_filename}")

            # 이미지 파일을 Base64로 인코딩
            with open(qr_filename, "rb") as image_file:
                base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")

            # Firestore에 Base64 문자열 저장
            workers_ref.document(worker_id).update({
                "qr_img_base64": base64_encoded
            })
            print(f"Firestore에 Base64 이미지 저장 완료: worker_id={worker_id}")

# Firestore 실시간 리스너 등록
query_watch = workers_ref.on_snapshot(on_snapshot)

print("Firestore 리스너 실행 중...")
try:
    # 프로그램이 종료되지 않도록 유지
    while True:
        pass
except KeyboardInterrupt:
    print("리스너 종료.")
