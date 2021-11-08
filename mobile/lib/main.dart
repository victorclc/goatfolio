import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/app.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/notification/firebase.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() async {
  F.appFlavor = Flavor.DEV;
  WidgetsFlutterBinding.ensureInitialized();
  await initializeFirebaseNotifications();
  final userService = UserService(
    F.cognitoUserPoolId,
    F.cognitoClientId,
    F.cognitoIdentityPoolId,
  );

  final app = new GoatfolioApp(
    hasValidSession: await userService.init(),
    userService: userService,
    prefs: await SharedPreferences.getInstance(),
  );
  runApp(app);
}
