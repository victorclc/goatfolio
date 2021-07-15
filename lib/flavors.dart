enum Flavor {
  DEV,
  PROD,
}

class F {
  static Flavor appFlavor;

  static String get title {
    switch (appFlavor) {
      case Flavor.DEV:
        return 'Goatfolio Dev';
      case Flavor.PROD:
        return 'Goatfolio';
      default:
        return 'title';
    }
  }

}
