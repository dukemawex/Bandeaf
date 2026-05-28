class ZoneCacheService {
  Map<String, dynamic> cachedGeoJson = const {'type': 'FeatureCollection', 'features': []};

  void updateCache(Map<String, dynamic> zoneCollection) {
    cachedGeoJson = zoneCollection;
  }
}
