import 'package:flutter/material.dart';

class SosButton extends StatelessWidget {
  const SosButton({super.key, required this.onPressed});

  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
      onPressed: onPressed,
      child: const Text('SOS'),
    );
  }
}
