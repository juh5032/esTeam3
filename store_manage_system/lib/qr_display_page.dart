import 'package:flutter/material.dart';
import 'dart:convert'; // Base64 디코딩용 패키지

class QRDisplayPage extends StatelessWidget {
  final String qrImageBase64;

  QRDisplayPage({required this.qrImageBase64});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, // 배경 검정색 설정
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // QR 코드 이미지 표시
            Image.memory(
              base64Decode(qrImageBase64),
              height: 300, // 원하는 크기로 설정
              width: 300,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context); // 이전 화면으로 돌아가기
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[800], // 버튼 색상
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10.0),
                ),
              ),
              child: Text(
                '돌아가기',
                style: TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
