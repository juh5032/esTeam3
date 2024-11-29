import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'login_page.dart'; // 로그인 화면 파일

void main() async {
  WidgetsFlutterBinding.ensureInitialized(); // 비동기 작업 설정
  await Firebase.initializeApp(); // Firebase 초기화
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Login System',
      home: LoginPage(), // 초기 화면을 로그인 페이지로 설정
    );
  }
}
