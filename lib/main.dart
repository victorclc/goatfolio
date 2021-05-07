import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:goatfolio/common/config/app_config.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/pages/navigation/screen/navigation.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/notification/firebase/firebase.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'common/theme/theme_changer.dart';

final cognitoClientId = '4eq433usu00k6m0as28srbsber';
final cognitoUserPoolId = 'us-east-2_tZFglntHx';
final cognitoIdentityPoolId =
    'arn:aws:cognito-idp:us-east-2:831967415635:userpool/us-east-2_tZFglntHx';

void main() async {
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

class GoatfolioApp extends StatelessWidget {
  final bool hasValidSession;
  final UserService userService;
  final SharedPreferences prefs;

  const GoatfolioApp(
      {Key key, this.hasValidSession, this.userService, this.prefs})
      : super(key: key);

  @override
  Widget build(context) {
    return ChangeNotifierProvider<ThemeChanger>(
      create: (_) => ThemeChanger(prefs),
      child: MaterialApp(
        title: 'Goatfolio',
        theme: ThemeData(),
        darkTheme: ThemeData.light(),
        localizationsDelegates: [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: [const Locale('pt', 'BR')],
        builder: (context, child) {
          return CupertinoTheme(
            data: Provider.of<ThemeChanger>(context).themeData,
            child: Material(child: child),
          );
        },
        home: Scaffold(
          body: hasValidSession
              ? buildNavigationPage(userService)
              : LoginPage(
                  userService: userService,
                  onLoggedOn: goToNavigationPage,
                ),
        ),
      ),
    );
  }
}
