from flask import Flask, render_template, request, jsonify
import threading
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
from app.qr_check_update_attendance import qr_check_update_attendance


# Flask 애플리케이션 생성
def create_app():
    app = Flask(__name__)

    # 기본 라우트
    @app.route('/')
    def index():
        return render_template('device.html')

    # QR 스캔 라우트
    @app.route('/start-qr-detection', methods=['POST'])
    def scan_qr():
        result = {}

        def run_qr_scanner():
            nonlocal result
            result = scan_qr_from_webcam()

        # QR 스캔을 별도 스레드에서 실행
        scan_thread = threading.Thread(target=run_qr_scanner)
        scan_thread.start()
        scan_thread.join()  # 스캔 완료를 기다림

        # 요청에서 출근/퇴근 모드 확인
        mode = request.args.get('mode', 'unknown')  # 'checkin' 또는 'checkout'


        # 스캔 결과를 반환
        if result["status"] == "success":

            qr_data = result["qr_data"]
            scan_time = result["scan_time"]
            action = "출근" if mode == "checkin" else "퇴근"
            # Firestore 업데이트 호출
            
            update_result = qr_check_update_attendance(qr_data, mode, scan_time)

            if update_result["status"] == "success":
                return jsonify({
                    "status": "success",
                    "message": f"{update_result['message']} (QR 데이터: {qr_data}, 스캔 시간: {result['scan_time']})"
                }), 200
            else:
                return jsonify({
                    "status": "failed",
                    "message": update_result["message"]
                }), 200
        else:
            return jsonify({
                "status": "failed",
                "message": "QR을 인식하지 못했습니다."
            }), 200

    return app


# 웹캠에서 QR 코드 스캔
def scan_qr_from_webcam(timeout=60):
    cap = cv2.VideoCapture(0)  # 웹캠 열기
    if not cap.isOpened():
        return {"status": "failed", "message": "웹캠을 열 수 없습니다."}

    print("QR 코드를 웹캠 앞에 보여주세요...")
    start_time = datetime.now()

    # OpenCV 창 속성 설정
    window_name = "QR 코드 스캐너"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # 창 크기 조정 가능
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)  # 창을 항상 맨 위로 설정
    cv2.resizeWindow(window_name, 800, 600)  # 창 크기 설정 (가로, 세로)
    cv2.moveWindow(window_name, 100, 100)  # 창 위치 설정 (x, y 좌표)

    while (datetime.now() - start_time).seconds < timeout:
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
            return {
                "status": "success",
                "qr_data": qr_data,
                "scan_time": scan_time
            }

        # QR 코드가 인식되지 않으면 계속 시도
        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):  # "q" 키로 수동 종료
            break

    # 타임아웃 발생
    cap.release()
    cv2.destroyAllWindows()
    print("QR을 인식하지 못했습니다.")
    return {"status": "failed", "message": "QR을 인식하지 못했습니다."}
