import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/app.dart';
import 'package:goatfolio/common/config/app_config.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/notification/firebase/firebase.dart';
import 'package:shared_preferences/shared_preferences.dart';


final cognitoClientId = '4eq433usu00k6m0as28srbsber';
final cognitoUserPoolId = 'us-east-2_tZFglntHx';
final cognitoIdentityPoolId =
    'arn:aws:cognito-idp:us-east-2:831967415635:userpool/us-east-2_tZFglntHx';

void main() async {
  F.appFlavor = Flavor.DEV;
  WidgetsFlutterBinding.ensureInitialized();
  await initializeFirebaseNotifications();
  final userService =
  UserService(cognitoUserPoolId, cognitoClientId, cognitoIdentityPoolId);

  final configuredApp = new AppConfig(
    cognitoClientId: cognitoClientId,
    cognitoUserPoolId: cognitoUserPoolId,
    cognitoIdentityPoolId: cognitoIdentityPoolId,
    child: new GoatfolioApp(
      hasValidSession: await userService.init(),
      userService: userService,
      prefs: await SharedPreferences.getInstance(),
    ),
  );

  runApp(configuredApp);
}


