import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Firebase Admin SDK 초기화
cred = credentials.Certificate("C:/Users/User/Desktop/db/raspteam33-firebase-adminsdk-maygo-0399ab2f21.json")
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 생성
db = firestore.client()

# stores 컬렉션의 store1 문서 안의 Schedules 컬렉션 참조
schedules_ref = db.collection('Stores').document('store1').collection('Schedules')

# 1월 1일부터 12월 31일까지 날짜 생성
start_date = datetime(2024, 1, 1)  # 원하는 해로 설정
end_date = datetime(2030, 12, 31)  # 동일한 해의 마지막 날짜

current_date = start_date

while current_date <= end_date:
    # 날짜를 "YYYY-MM-DD" 형식의 문자열로 변환
    doc_name = current_date.strftime("%Y-%m-%d")

    # Firestore에 문서 생성
    schedules_ref.document(doc_name).set({
        "placeholder": True  # 원하는 필드와 데이터를 추가할 수 있음
    })

    # 다음 날짜로 이동
    current_date += timedelta(days=1)

print("문서 생성 완료!")
