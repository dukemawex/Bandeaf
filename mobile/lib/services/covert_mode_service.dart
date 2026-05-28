class CovertModeService {
  int _volumeDownPressCount = 0;

  bool registerVolumeDownPress() {
    _volumeDownPressCount += 1;
    if (_volumeDownPressCount >= 3) {
      _volumeDownPressCount = 0;
      return true;
    }
    return false;
  }
}
