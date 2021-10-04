import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:firebase_analytics/observer.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:goatfolio/global.dart' as bloc;
import 'package:goatfolio/pages/login/login.dart';
import 'package:goatfolio/theme/theme_changer.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'authentication/cognito.dart';
import 'flavors.dart';

class GoatfolioApp extends StatelessWidget {
  final FirebaseAnalytics analytics = FirebaseAnalytics();
  final bool hasValidSession;
  final UserService userService;
  final SharedPreferences prefs;

  GoatfolioApp(
      {Key? key,
      required this.hasValidSession,
      required this.userService,
      required this.prefs})
      : super(key: key);

  @override
  Widget build(context) {
    return MultiProvider(
      providers: [
        Provider(create: (_) => userService),
        ChangeNotifierProvider<ThemeChanger>(
          create: (_) => ThemeChanger(prefs),
        )
      ],
      child: MultiBlocProvider(
        providers: bloc.buildGlobalProviders(),
        child: Consumer<ThemeChanger>(
          builder: (context, model, _) => MaterialApp(
            title: F.title,
            navigatorObservers: [
              FirebaseAnalyticsObserver(analytics: analytics),
            ],
            theme: model.androidTheme,
            darkTheme: model.androidDarkThemeData,
            localizationsDelegates: [
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            supportedLocales: [const Locale('pt', 'BR')],
            builder: (context, child) {
              return CupertinoTheme(
                data: model.themeData,
                child: Material(child: child),
              );
            },
            home: Scaffold(
              body:
                  // ? buildNavigationPage(userService)
                  LoginPage(
                      userService: userService,
                      onLoggedOn: () => 1,
                    ),
            ),
          ),
        ),
      ),
    );
  }
}
