import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import threading

# Firebase Admin SDK 초기화
cred = credentials.Certificate("C:/Users/User/Desktop/db/raspteam33-firebase-adminsdk-maygo-0399ab2f21.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 현재 월의 모든 날짜 리스트 생성
def get_current_month_dates():
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1)
    next_month = first_day + timedelta(days=32)
    last_day = datetime(next_month.year, next_month.month, 1) - timedelta(days=1)
    dates = [(first_day + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((last_day - first_day).days + 1)]
    return dates

# Workers 컬렉션을 감지하고 근무시간 하위 컬렉션에 리스너 추가
def listen_to_workers():
    workers_ref = db.collection('Stores').document('store1').collection('Workers')

    # Workers 리스너 콜백
    def on_worker_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            worker_id = change.document.id
            if change.type.name in ["ADDED", "MODIFIED"]:
                print(f"Worker updated: {worker_id}")
                listen_to_work_hours(worker_id)
            elif change.type.name == "REMOVED":
                print(f"Worker removed: {worker_id}")
                # 삭제된 문서 데이터 확보
                worker_data = change.document.to_dict()
                if worker_data:
                    worker_name = worker_data.get("이름", f"Unknown_{worker_id}")
                    remove_worker_from_schedules(worker_name)


    # Workers 컬렉션에 리스너 추가
    workers_ref.on_snapshot(on_worker_snapshot)

# 근무시간 하위 컬렉션의 변경 사항 감지
def listen_to_work_hours(worker_id):
    work_hours_ref = db.collection('Stores').document('store1').collection('Workers').document(worker_id).collection('근무시간')

    # 근무시간 리스너 콜백
    def on_work_hours_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name in ["ADDED", "MODIFIED"]:
                day = change.document.id  # 요일 (monday, tuesday, ...)
                work_hours = change.document.to_dict()
                print(f"Work hours updated for {worker_id} on {day}: {work_hours}")
                update_schedule_for_day(worker_id, day, work_hours)
                
            elif change.type.name == "REMOVED":
                print(f"Work hours removed for {worker_id}")
                remove_worker_from_schedules(worker_id)

    # 근무시간 하위 컬렉션에 리스너 추가
    work_hours_ref.on_snapshot(on_work_hours_snapshot)

# Schedules 컬렉션 업데이트 (특정 요일에 대한 변경만 처리)
def update_schedule_for_day(worker_id, day, work_hours):
    schedules_ref = db.collection('Stores').document('store1').collection('Schedules')
    dates = get_current_month_dates()
    worker_name = db.collection('Stores').document('store1').collection('Workers').document(worker_id).get().to_dict().get("이름", f"Unknown_{worker_id}")

    start_time = work_hours.get("출근")
    end_time = work_hours.get("퇴근")

    # 현재 월의 모든 날짜 중에서 요일(day)과 일치하는 날짜 업데이트
    for date in dates:
        if datetime.strptime(date, "%Y-%m-%d").strftime("%A").lower() == day:
            schedules_ref.document(date).set({
                worker_name: f"{start_time}~{end_time}"
            }, merge=True)
            print(f"Updated schedule for {date}: {worker_name} -> {start_time}~{end_time}")

# Schedules에서 특정 worker의 데이터를 제거
def remove_worker_from_schedules(worker_name):
    schedules_ref = db.collection('Stores').document('store1').collection('Schedules')

    # 현재 월의 날짜 리스트 가져오기
    current_month_dates = get_current_month_dates()

    # 현재 달에 해당하는 Schedules 문서만 삭제 처리
    for date in current_month_dates:
        doc_ref = schedules_ref.document(date)
        doc_data = doc_ref.get().to_dict()  # 문서 데이터를 가져옴

        if doc_data and worker_name in doc_data:  # 삭제 대상이 문서에 존재할 경우
            print(f"Removing {worker_name} from schedule on {date}")
            doc_ref.update({
                worker_name: firestore.DELETE_FIELD  # Firestore에서 필드 삭제
            })
            print(f"Removed {worker_name} from schedule on {date}")


# 프로그램 시작
if __name__ == "__main__":
    print("Firestore Listener is Running...")
    # Workers 리스너를 별도의 스레드에서 실행
    threading.Thread(target=listen_to_workers, daemon=True).start()

    # 메인 스레드 대기 (무한 루프 유지)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Listener stopped.")
