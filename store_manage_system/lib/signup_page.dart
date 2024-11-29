import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class SignUpPage extends StatefulWidget {
  @override
  _SignUpPageState createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // 입력 필드 컨트롤러
  final TextEditingController _idController = TextEditingController();
  final TextEditingController _pwdController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();
  String? _selectedStore; // 선택된 점포명
  String? _selectedPosition; // 선택된 직책
  String? _idValidationMessage; // ID 검증 메시지

  // Firestore에서 ID 중복 체크
  Future<void> checkIdAvailability(String id) async {
    if (id.isEmpty) {
      setState(() {
        _idValidationMessage = null;
      });
      return;
    }

    try {
      DocumentSnapshot doc = await _firestore.collection('Login').doc(id).get();
      setState(() {
        if (doc.exists) {
          _idValidationMessage = '이미 사용 중인 ID입니다.';
        } else {
          _idValidationMessage = '사용 가능한 ID입니다!';
        }
      });
    } catch (e) {
      setState(() {
        _idValidationMessage = 'ID 확인 중 오류 발생';
      });
    }
  }

  // Firestore에 회원가입 데이터 저장
  Future<void> signUp() async {
    final String id = _idController.text.trim();
    final String pwd = _pwdController.text.trim();
    final String name = _nameController.text.trim();

    if (id.isEmpty ||
        pwd.isEmpty ||
        name.isEmpty ||
        _selectedStore == null ||
        _selectedPosition == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('모든 필드를 입력해주세요.')),
      );
      return;
    }

    if (pwd.length != 4 || int.tryParse(pwd) == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('비밀번호는 숫자 4자리여야 합니다.')),
      );
      return;
    }

    try {
      DocumentSnapshot doc = await _firestore.collection('Login').doc(id).get();
      if (doc.exists) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('이미 존재하는 ID입니다.')),
        );
        return;
      }

      // Firestore에 데이터 저장
      await _firestore.collection('Login').doc(id).set({
        'pwd': pwd,
        'name': name,
        'store': _selectedStore,
        'position': _selectedPosition,
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('회원가입 완료!')),
      );

      // 로그인 화면으로 이동
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('회원가입 중 오류 발생: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('회원가입'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ID 입력 및 검증
              TextField(
                controller: _idController,
                decoration: InputDecoration(labelText: 'ID'),
                onChanged: (value) {
                  checkIdAvailability(value); // ID 중복 체크
                },
              ),
              if (_idValidationMessage != null)
                Text(
                  _idValidationMessage!,
                  style: TextStyle(
                    color: _idValidationMessage == '사용 가능한 ID입니다!'
                        ? Colors.blue
                        : Colors.red,
                  ),
                ),
              SizedBox(height: 10),

              // 비밀번호 입력
              TextField(
                controller: _pwdController,
                decoration: InputDecoration(labelText: '비밀번호 (숫자 4자리)'),
                obscureText: true,
                keyboardType: TextInputType.number,
              ),
              SizedBox(height: 10),

              // 이름 입력
              TextField(
                controller: _nameController,
                decoration: InputDecoration(labelText: '이름'),
              ),
              SizedBox(height: 10),

              // 점포 선택
              FutureBuilder<QuerySnapshot>(
                future: _firestore.collection('Stores').get(),
                builder: (context, snapshot) {
                  if (!snapshot.hasData) {
                    return CircularProgressIndicator();
                  }

                  List<DropdownMenuItem<String>> storeItems =
                      snapshot.data!.docs.map((doc) {
                    String storeName = doc['점포명'];
                    return DropdownMenuItem<String>(
                      value: storeName,
                      child: Text(storeName),
                    );
                  }).toList();

                  return DropdownButton<String>(
                    value: _selectedStore,
                    hint: Text('점포를 선택하세요'),
                    items: storeItems,
                    onChanged: (value) {
                      setState(() {
                        _selectedStore = value;
                      });
                    },
                  );
                },
              ),
              SizedBox(height: 10),

              // 직책 선택
              DropdownButton<String>(
                value: _selectedPosition,
                hint: Text('직책을 선택하세요'),
                items: [
                  DropdownMenuItem(value: '알바', child: Text('알바')),
                  DropdownMenuItem(value: '사장', child: Text('사장')),
                ],
                onChanged: (value) {
                  setState(() {
                    _selectedPosition = value;
                  });
                },
              ),
              SizedBox(height: 20),

              // 회원가입 버튼
              Center(
                child: ElevatedButton(
                  onPressed: signUp,
                  child: Text('회원가입'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
