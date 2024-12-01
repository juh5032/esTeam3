import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:convert'; // Base64 인코딩 및 디코딩을 위한 패키지
import 'signup_page.dart'; // 회원가입 페이지 가져오기
import 'qr_display_page.dart';

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // 입력 컨트롤러
  final TextEditingController _idController = TextEditingController();
  final TextEditingController _pwdController = TextEditingController();

  String? qrImageBase64; // 최종적으로 가져온 QR 코드 데이터를 저장

  Future<void> login() async {
    final String id = _idController.text.trim();
    final String pwd = _pwdController.text.trim();

    if (id.isEmpty || pwd.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('ID와 비밀번호를 입력하세요.')),
      );
      return;
    }

    try {
      // Step 1: Login 컬렉션에서 ID에 해당하는 문서 가져오기
      DocumentSnapshot userDoc =
          await _firestore.collection('login').doc(id).get();

      if (!userDoc.exists) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('존재하지 않는 ID입니다.')),
        );
        return;
      }

      // 비밀번호 확인
      Map<String, dynamic> userData = userDoc.data() as Map<String, dynamic>;
      if (userData['pwd'] != pwd) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('비밀번호가 틀렸습니다.')),
        );
        return;
      }

      // Step 2: workers 컬렉션에서 name 필드와 일치하는 문서 검색
      String userName = userData['name'];

      QuerySnapshot workersQuery = await _firestore
          .collection('workers')
          .where('name', isEqualTo: userName)
          .get();

      if (workersQuery.docs.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('근무자 정보를 찾을 수 없습니다.')),
        );
        return;
      }

      // Step 3: qr_img_base64 값 가져오기
      Map<String, dynamic> workerData =
          workersQuery.docs.first.data() as Map<String, dynamic>;
      String qrImageBase64 = workerData['qr_img_base64'];

      // QR 코드 화면으로 이동
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => QRDisplayPage(qrImageBase64: qrImageBase64),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('로그인 중 오류 발생: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(''),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 250, // 원하는 너비로 설정
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Login',
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 25,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 10),
                  TextField(
                    controller: _idController,
                    decoration: InputDecoration(labelText: '사용자 이름'),
                  ),
                  SizedBox(height: 20),
                  TextField(
                    controller: _pwdController,
                    decoration: InputDecoration(labelText: '비밀번호'),
                    obscureText: true,
                  ),
                ],
              ),
            ),
            SizedBox(height: 35),
            Container(
              width: 200,
              child: ElevatedButton(
                onPressed: login,
                child: Text(
                  '로그인',
                  style: TextStyle(color: Colors.white),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color.fromARGB(255, 231, 109, 109),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10.0),
                  ),
                ),
              ),
            ),
            SizedBox(height: 10), // 버튼과 간격 조정
            Container(
              width: 280,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  TextButton(
                    onPressed: () {
                      // 아이디/비밀번호 찾기 로직 추가 가능
                    },
                    child: Text(
                      '아이디/비밀번호 찾기',
                      style: TextStyle(
                        color: const Color.fromARGB(255, 175, 174, 174),
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      // 회원가입 페이지로 이동
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => SignUpPage()),
                      );
                    },
                    child: Text(
                      '회원가입',
                      style: TextStyle(color: Colors.blue),
                    ),
                  )
                ],
              ),
            ),
            SizedBox(height: 20),
            if (qrImageBase64 != null)
              Column(
                children: [
                  Text('QR 코드:'),
                  Image.memory(
                    // Base64 문자열을 이미지로 변환
                    base64Decode(qrImageBase64!),
                    height: 200,
                    width: 200,
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
