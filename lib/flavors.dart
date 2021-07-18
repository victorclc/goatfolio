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
        return '4eq433usu00k6m0as28srbsber';
    }
  }

  static String get cognitoUserPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'sa-east-1_eGtDKQt4X';
      case Flavor.DEV:
      default:
        return 'us-east-2_tZFglntHx';
    }
  }

  static String get cognitoIdentityPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'arn:aws:cognito-idp:sa-east-1:810300526230:userpool/sa-east-1_eGtDKQt4X';
      case Flavor.DEV:
      default:
        return 'arn:aws:cognito-idp:us-east-2:831967415635:userpool/us-east-2_tZFglntHx';
    }
  }

  static String get baseUrl {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'https://api.goatfolio.com.br/';
      case Flavor.DEV:
      default:
        return 'https://dev.victorclc.com.br/';
    }
  }
}
