class DeadmanService {
  int checkinIntervalSeconds = 3600;

  void snooze() {
    checkinIntervalSeconds += 900;
  }
}
