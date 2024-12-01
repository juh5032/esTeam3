import cv2
from pyzbar.pyzbar import decode
from datetime import datetime

# 웹캠에서 QR 코드 스캔
def scan_qr_from_webcam():
    cap = cv2.VideoCapture(0)  # 웹캠 열기
    print("QR 코드를 웹캠 앞에 보여주세요...")

    while True:
        ret, frame = cap.read()  # 프레임 읽기
        if not ret:
            print("웹캠에서 이미지를 읽을 수 없습니다.")
            break

        # QR 코드 디코딩
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")  # QR 코드 데이터
            scan_time = datetime.now()  # 현재 시간
            print(f"스캔된 QR 데이터: {qr_data}")
            print(f"스캔된 시간: {scan_time}")

            # 작업 종료
            cap.release()
            cv2.destroyAllWindows()
            return

        # QR 코드가 인식되지 않으면 계속 시도
        cv2.imshow("QR 코드 스캐너", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):  # "q" 키로 수동 종료
            break

    cap.release()
    cv2.destroyAllWindows()

# 실행
scan_qr_from_webcam()
