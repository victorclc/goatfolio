enum Flavor {
  DEV,
  PROD,
}

class F {
  static Flavor appFlavor;

  static String get title {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'Goatfolio';
      case Flavor.DEV:
      default:
        return 'Goatfolio Dev';
    }
  }

  static String get cognitoClientId {
    switch (appFlavor) {
      case Flavor.PROD:
        return '7ovg7avdp7r6s02kpc6oc6hl04';
      case Flavor.DEV:
      default:
        return '30mcm6342c56fj7da8cqmns2f0';
    }
  }

  static String get cognitoUserPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'sa-east-1_eGtDKQt4X';
      case Flavor.DEV:
      default:
        return 'sa-east-1_PhDIztXK0';
    }
  }

  static String get cognitoIdentityPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'arn:aws:cognito-idp:sa-east-1:810300526230:userpool/sa-east-1_eGtDKQt4X';
      case Flavor.DEV:
      default:
        return 'arn:aws:cognito-idp:sa-east-1:138414734174:userpool/sa-east-1_PhDIztXK0';
    }
  }

  static String get baseUrl {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'https://api.goatfolio.com.br/';
      case Flavor.DEV:
      default:
        return 'https://dev.goatfolio.com.br/';
    }
  }
}
