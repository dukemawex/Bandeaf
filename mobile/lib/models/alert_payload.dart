class AlertPayload {
  AlertPayload({
    required this.userId,
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.timestamp,
    this.batteryLevel,
    this.message,
  });

  final String userId;
  final String name;
  final double? latitude;
  final double? longitude;
  final DateTime timestamp;
  final int? batteryLevel;
  final String? message;
}
