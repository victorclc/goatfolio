enum Flavor {
  DEV,
  PROD,
}

class F {
  static late Flavor appFlavor;

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
        return '3gcs81tod4nb9hhfkipj4plsvp';
      case Flavor.DEV:
      default:
        return '30mcm6342c56fj7da8cqmns2f0';
    }
  }

  static String get cognitoFederatedClientId {
    switch (appFlavor) {
      case Flavor.PROD:
        return '2svfk9vab5pp78t8lvc5nit5nn';
      case Flavor.DEV:
      default:
        return '3osrp00oi50q2va95o3m43kjmi';
    }
  }

  static String get cognitoUserPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'sa-east-1_kPXadCr4Z';
      case Flavor.DEV:
      default:
        return 'sa-east-1_PhDIztXK0';
    }
  }

  static String get cognitoFederatedUserPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'sa-east-1_qf0cC9q0N';
      case Flavor.DEV:
      default:
        return 'sa-east-1_8hFn2wdZ4';
    }
  }

  static String get cognitoIdentityPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'arn:aws:cognito-idp:sa-east-1:810300526230:userpool/sa-east-1_kPXadCr4Z';
      case Flavor.DEV:
      default:
        return 'arn:aws:cognito-idp:sa-east-1:138414734174:userpool/sa-east-1_PhDIztXK0';
    }
  }

  static String get cognitoFederatedIdentityPoolId {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'arn:aws:cognito-idp:sa-east-1:810300526230:userpool/sa-east-1_qf0cC9q0N';
      case Flavor.DEV:
      default:
        return 'arn:aws:cognito-idp:sa-east-1:138414734174:userpool/sa-east-1_8hFn2wdZ4';
    }
  }

  static String get cognitoDomainName {
    switch (appFlavor) {
      case Flavor.PROD:
        return 'https://goatfolio-dev.auth.sa-east-1.amazoncognito.com';
      case Flavor.DEV:
      default:
        return 'https://goatfolio-dev.auth.sa-east-1.amazoncognito.com';
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

  static String get appLogo => "images/logo/logo.png";
}
