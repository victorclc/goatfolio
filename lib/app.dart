import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:firebase_analytics/observer.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/pages/navigation/screen/navigation.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/cubit/performance_cubit.dart';
import 'package:goatfolio/services/performance/cubit/summary_cubit.dart';
import 'package:goatfolio/services/vandelay/cubit/vandelay_cubit.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'common/theme/theme_changer.dart';
import 'flavors.dart';

class GoatfolioApp extends StatelessWidget {
  final FirebaseAnalytics analytics = FirebaseAnalytics();
  final bool hasValidSession;
  final UserService userService;
  final SharedPreferences prefs;

  GoatfolioApp({Key key, this.hasValidSession, this.userService, this.prefs})
      : super(key: key);

  ThemeData androidDarkThemeData(BuildContext context, ThemeChanger theme) {
    if (theme.configuredTheme == null ||
        theme.configuredTheme == ThemeChanger.CFG_AUTOMATIC_VALUE) {
      return ThemeData(
          brightness: Brightness.dark,
          backgroundColor: CupertinoColors.black,
          scaffoldBackgroundColor: CupertinoColors.black);
    }
    return null;
  }

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
        providers: [
          BlocProvider<SummaryCubit>(
            create: (_) => SummaryCubit(userService),
          ),
          BlocProvider<PerformanceCubit>(
            create: (_) => PerformanceCubit(userService),
          ),
          BlocProvider<VandelayPendencyCubit>(
            create: (_) => VandelayPendencyCubit(userService),
          ),
        ],
        child: Consumer<ThemeChanger>(
          builder: (context, model, _) => MaterialApp(
            title: F.title,
            navigatorObservers: [
              FirebaseAnalyticsObserver(analytics: analytics),
            ],
            theme: model.androidTheme,
            darkTheme: androidDarkThemeData(context, model),
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
              body: hasValidSession
                  ? buildNavigationPage(userService)
                  : LoginPage(
                      userService: userService,
                      onLoggedOn: goToNavigationPage,
                    ),
            ),
          ),
        ),
      ),
    );
  }
}
