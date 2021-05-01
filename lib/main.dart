import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:goatfolio/common/config/app_config.dart';
import 'package:goatfolio/pages/add/screen/add.dart';
import 'package:goatfolio/pages/extract/extract.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/pages/portfolio/screen/portfolio.dart';
import 'package:goatfolio/pages/settings/screen/settings_page.dart';
import 'package:goatfolio/pages/summary/screen/summary.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_summary_notifier.dart';
import 'package:keyboard_visibility/keyboard_visibility.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

import 'common/theme/theme_changer.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  FirebaseMessaging messaging = FirebaseMessaging.instance;
  NotificationSettings settings = await messaging.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false,
    provisional: false,
    sound: true,
  );
  await FirebaseMessaging.instance.setForegroundNotificationPresentationOptions(
    alert: true, // Required to display a heads up notification
    badge: true,
    sound: true,
  );

  print("APN TOKEN");
  print(await FirebaseMessaging.instance.getAPNSToken());
  print(await FirebaseMessaging.instance.getToken());
  final cognitoClientId = '4eq433usu00k6m0as28srbsber';
  final cognitoUserPoolId = 'us-east-2_tZFglntHx';
  final cognitoIdentityPoolId =
      'arn:aws:cognito-idp:us-east-2:831967415635:userpool/us-east-2_tZFglntHx';
  final userService =
      UserService(cognitoUserPoolId, cognitoClientId, cognitoIdentityPoolId);
  final hasValidSession = await userService.init();
  SharedPreferences prefs = await SharedPreferences.getInstance();
  final configuredApp = new AppConfig(
    cognitoClientId: cognitoClientId,
    cognitoUserPoolId: cognitoUserPoolId,
    cognitoIdentityPoolId: cognitoIdentityPoolId,
    child: new GoatfolioApp(
        hasValidSession: hasValidSession,
        userService: userService,
        prefs: prefs),
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

Widget buildNavigationPage(UserService userService) {
  return MultiProvider(
    child: NavigationWidget(),
    providers: [
      Provider(
        create: (context) => userService,
      ),
      ChangeNotifierProvider(create: (_) => PortfolioListNotifier(userService)),
      ChangeNotifierProvider(
          create: (_) => PortfolioSummaryNotifier(userService))
    ],
  );
}

void goToNavigationPage(BuildContext context, UserService userService) async {
  await Navigator.pushReplacement(
    context,
    CupertinoPageRoute(
      builder: (context) => buildNavigationPage(userService),
    ),
  );
}

class NavigationWidget extends StatefulWidget {
  @override
  _NavigationWidgetState createState() => _NavigationWidgetState();
}

class InvisibleCupertinoTabBar extends CupertinoTabBar {
  static const dummyIcon = Icon(IconData(0x0020));

  InvisibleCupertinoTabBar(backGroundColor)
      : super(
          backgroundColor: backGroundColor,
          items: [
            BottomNavigationBarItem(icon: dummyIcon),
            BottomNavigationBarItem(icon: dummyIcon),
            BottomNavigationBarItem(icon: dummyIcon),
            BottomNavigationBarItem(icon: dummyIcon),
            BottomNavigationBarItem(icon: dummyIcon),
          ],
        );

  @override
  CupertinoTabBar copyWith({
    Key key,
    List<BottomNavigationBarItem> items,
    Color backgroundColor,
    Color activeColor,
    Color inactiveColor,
    double iconSize,
    Border border,
    int currentIndex,
    ValueChanged<int> onTap,
  }) =>
      InvisibleCupertinoTabBar(backgroundColor);

  @override
  Size get preferredSize => const Size.square(0);

  @override
  Widget build(BuildContext context) => Container();
}

class _NavigationWidgetState extends State<NavigationWidget>
    with SingleTickerProviderStateMixin {
  CupertinoTabController controller;
  bool isKeyboardVisible = false;
  int currentIndex = 0;
  List<CupertinoTabView> tabViews;

  @override
  void initState() {
    super.initState();
    controller = new CupertinoTabController();

    KeyboardVisibilityNotification().addNewListener(
      onChange: (bool isVisible) {
        setState(() => isKeyboardVisible = isVisible);
      },
    );

    tabViews = [
      CupertinoTabView(
        defaultTitle: SummaryPage.title,
        builder: (context) {
          return SummaryPage();
        },
        navigatorKey: GlobalKey<NavigatorState>(),
      ),
      CupertinoTabView(
        defaultTitle: PortfolioPage.title,
        builder: (context) => PortfolioPage(),
        navigatorKey: GlobalKey<NavigatorState>(),
      ),
      CupertinoTabView(
        defaultTitle: AddPage.title,
        builder: (context) => AddPage(),
        navigatorKey: GlobalKey<NavigatorState>(),
      ),
      CupertinoTabView(
        defaultTitle: ExtractPage.title,
        builder: (context) => ExtractPage(),
        navigatorKey: GlobalKey<NavigatorState>(),
      ),
      CupertinoTabView(
        defaultTitle: SettingsPage.title,
        builder: (context) => SettingsPage(),
        navigatorKey: GlobalKey<NavigatorState>(),
      )
    ];
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(context) {
    return CupertinoTabScaffold(
      controller: controller,
      resizeToAvoidBottomInset: false,
      tabBar: isKeyboardVisible
          ? InvisibleCupertinoTabBar(
              CupertinoTheme.of(context).scaffoldBackgroundColor)
          : CupertinoTabBar(
              onTap: (index) {
                if (index == currentIndex) {
                  Navigator.of(tabViews[index].navigatorKey.currentContext)
                      .popUntil((route) => route.isFirst);
                }
                currentIndex = index;
              },
              items: [
                BottomNavigationBarItem(
                    label: SummaryPage.title, icon: SummaryPage.icon),
                BottomNavigationBarItem(
                    label: PortfolioPage.title, icon: PortfolioPage.icon),
                BottomNavigationBarItem(
                    label: AddPage.title, icon: AddPage.icon),
                BottomNavigationBarItem(
                    label: ExtractPage.title, icon: ExtractPage.icon),
                BottomNavigationBarItem(
                    label: SettingsPage.title, icon: SettingsPage.icon),
              ],
            ),
      tabBuilder: (context, index) {
        switch (index) {
          case 0:
            return tabViews[0];
          case 1:
            return tabViews[1];
          case 2:
            return tabViews[2];
          case 3:
            return tabViews[3];
          case 4:
            return tabViews[4];
          default:
            assert(false, 'Unexpected tab');
            return null;
        }
      },
    );
  }
}
