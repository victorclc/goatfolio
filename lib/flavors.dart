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
        return '4eq433usu00k6m0as28srbsber';
      case Flavor.DEV:
      default:
        return '4eq433usu00k6m0as28srbsber';
    }
  }

  static String get cognitoUserPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'us-east-2_tZFglntHx';
      case Flavor.DEV:
      default:
        return 'us-east-2_tZFglntHx';
    }
  }

  static String get cognitoIdentityPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'arn:aws:cognito-idp:us-east-2:831967415635:userpool/us-east-2_tZFglntHx';
      case Flavor.DEV:
      default:
        return 'arn:aws:cognito-idp:us-east-2:831967415635:userpool/us-east-2_tZFglntHx';
    }
  }
}
