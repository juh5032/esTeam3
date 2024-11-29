import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:convert'; // Base64 인코딩 및 디코딩을 위한 패키지
import 'signup_page.dart'; // 회원가입 페이지 가져오기

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
          await _firestore.collection('Login').doc(id).get();

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

      // Step 2: name과 store 값 가져오기
      String userName = userData['name'];
      String userStore = userData['store'];

      // Step 3: Stores 컬렉션에서 store 필드와 일치하는 문서 검색
      QuerySnapshot storeQuery = await _firestore.collection('Stores').get();
      DocumentSnapshot? targetStoreDoc;

      for (var doc in storeQuery.docs) {
        Map<String, dynamic> storeData = doc.data() as Map<String, dynamic>;
        if (storeData['점포명'] == userStore) {
          targetStoreDoc = doc;
          break;
        }
      }

      if (targetStoreDoc == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('점포 정보를 찾을 수 없습니다.')),
        );
        return;
      }

      // Step 4: Workers 컬렉션에서 name과 일치하는 문서 검색
      QuerySnapshot workersQuery = await targetStoreDoc.reference
          .collection('Workers')
          .where('이름', isEqualTo: userName)
          .get();

      if (workersQuery.docs.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('근무자 정보를 찾을 수 없습니다.')),
        );
        return;
      }

      // Step 5: qr_img_base64 값 가져오기
      Map<String, dynamic> workerData =
          workersQuery.docs.first.data() as Map<String, dynamic>;
      setState(() {
        qrImageBase64 = workerData['qr_img_base64'];
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('로그인 성공!')),
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
        title: Text('로그인'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _idController,
              decoration: InputDecoration(labelText: 'ID'),
            ),
            TextField(
              controller: _pwdController,
              decoration: InputDecoration(labelText: '비밀번호'),
              obscureText: true,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: login,
              child: Text('로그인'),
            ),
            TextButton(
              onPressed: () {
                // 회원가입 페이지로 이동
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => SignUpPage()),
                );
              },
              child: Text('회원가입'),
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
