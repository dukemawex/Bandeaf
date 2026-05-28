import 'package:flutter/material.dart';

import '../services/alert_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final AlertService _alertService = AlertService();
  String _status = 'Ready';

  Future<void> _sendSos() async {
    final result = await _alertService.triggerSos();
    if (!mounted) return;
    setState(() => _status = result);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Family Connect')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('SAFE-NET Emergency Console', textAlign: TextAlign.center),
            const SizedBox(height: 24),
            SizedBox(
              width: 220,
              height: 220,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
                onPressed: _sendSos,
                child: const Text('SOS', style: TextStyle(fontSize: 44, fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 20),
            Text('Status: $_status'),
          ],
        ),
      ),
    );
  }
}
