import subprocess
import threading
from app import create_app

# Flask 애플리케이션 생성
app = create_app()

# qr_gen_by_update.py 실행
def run_qr_gen_independently():
    process = subprocess.Popen(
        ["python", "qr_gen_by_update.py"],
        stdout=subprocess.PIPE,  # 출력 캡처
        stderr=subprocess.PIPE   # 오류도 캡처
    )

    # 실시간 로그 출력 (stdout, stderr 통합)
    def log_output():
        for line in iter(process.stdout.readline, b''):
            print(f"QR GEN: {line.decode().strip()}")  # 표준 출력
        for line in iter(process.stderr.readline, b''):
            print(f"QR GEN ERROR: {line.decode().strip()}")  # 오류 출력

    # stdout, stderr 로그 출력 스레드 실행
    threading.Thread(target=log_output, daemon=True).start()

# 메인 실행 함수
if __name__ == "__main__":
    # qr_gen_by_update.py 실행 (로그 출력)
    threading.Thread(target=run_qr_gen_independently, daemon=True).start()

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000, debug=True)
