import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:firebase_analytics/observer.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/pages/navigation/screen/navigation.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'common/theme/theme_changer.dart';
import 'flavors.dart';


class GoatfolioApp extends StatelessWidget {
  final FirebaseAnalytics analytics = FirebaseAnalytics();
  final bool hasValidSession;
  final UserService userService;
  final SharedPreferences prefs;

  GoatfolioApp(
      {Key key, this.hasValidSession, this.userService, this.prefs})
      : super(key: key);

  @override
  Widget build(context) {
    return ChangeNotifierProvider<ThemeChanger>(
      create: (_) => ThemeChanger(prefs),
      child: MaterialApp(
        title: F.title,
        navigatorObservers: [
          FirebaseAnalyticsObserver(analytics: analytics),
        ],
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