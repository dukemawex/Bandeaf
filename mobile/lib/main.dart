import 'package:flutter/material.dart';

import 'screens/home_screen.dart';

void main() {
  runApp(const SafeNetApp());
}

class SafeNetApp extends StatelessWidget {
  const SafeNetApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Family Connect',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.red),
      home: const HomeScreen(),
    );
  }
}
