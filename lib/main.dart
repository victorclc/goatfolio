import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:goatfolio/authentication/screen/login.dart';
import 'package:goatfolio/common/config/app_config.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final configuredApp = new AppConfig(
      cognitoClientId: '4eq433usu00k6m0as28srbsber',
      cognitoUserPoolId: 'us-east-2_tZFglntHx',
      cognitoIdentityPoolId:
      'arn:aws:cognito-idp:us-east-2:831967415635:userpool/us-east-2_tZFglntHx',
      child: new GoatfolioApp(),
  );
  runApp(configuredApp);
}

class GoatfolioApp extends StatelessWidget {
  @override
  Widget build(context) {
    return MaterialApp(
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
          data: CupertinoThemeData(brightness: Brightness.light),
          child: Material(child: child),
        );
      },
      home: LoginPage(onLoggedOn: (userService) => Container(),),
    );
  }
}