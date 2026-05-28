import 'dart:convert';

import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

class AlertService {
  Future<String> triggerSos() async {
    final position = await _getPosition();
    final payload = {
      'gps_coords': {
        'lat': position?.latitude,
        'lon': position?.longitude,
        'accuracy': position?.accuracy,
      },
      'alert_type': 'SOS',
      'battery_level': null,
      'message': 'Emergency triggered from mobile app',
    };

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/v1/alert/sos'),
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer DEMO_TOKEN'},
        body: jsonEncode(payload),
      );
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return 'SOS sent';
      }
      return 'Failed (${response.statusCode})';
    } catch (_) {
      return 'Offline fallback required (SMS/Mesh)';
    }
  }

  Future<Position?> _getPosition() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return null;
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.deniedForever || permission == LocationPermission.denied) {
      return null;
    }
    return Geolocator.getCurrentPosition();
  }
}
