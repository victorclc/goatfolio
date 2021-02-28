import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:goatfolio/account/screen/account.dart';
import 'package:goatfolio/add/screen/add.dart';
import 'package:goatfolio/authentication/screen/login.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/config/app_config.dart';
import 'package:goatfolio/extract/screen/screen.dart';
import 'package:goatfolio/portfolio/screen/portfolio.dart';
import 'package:goatfolio/summary/screen/summary.dart';
import 'package:keyboard_visibility/keyboard_visibility.dart';
import 'package:provider/provider.dart';

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
      home: Scaffold(
        body: LoginPage(
          onLoggedOn: goToNavigationPage,
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
    ],
  );
}

void goToNavigationPage(BuildContext context, UserService userService) async {
  await Navigator.pushReplacement(
    context,
    MaterialPageRoute(
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

  InvisibleCupertinoTabBar()
      : super(
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
      InvisibleCupertinoTabBar();

  @override
  Size get preferredSize => const Size.square(0);

  @override
  Widget build(BuildContext context) => Container();
}

class _NavigationWidgetState extends State<NavigationWidget>
    with SingleTickerProviderStateMixin {
  TabController controller;
  bool isKeyboardVisible = false;

  @override
  void initState() {
    super.initState();
    controller = new TabController(vsync: this, length: 5);

    KeyboardVisibilityNotification().addNewListener(
      onChange: (bool isVisible) {
        setState(() => isKeyboardVisible = isVisible);
      },
    );
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(context) {
    return CupertinoTabScaffold(
      resizeToAvoidBottomInset: false,
      tabBar: isKeyboardVisible
          ? InvisibleCupertinoTabBar()
          : CupertinoTabBar(
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
                    label: AccountPage.title, icon: AccountPage.icon),
              ],
            ),
      tabBuilder: (context, index) {
        switch (index) {
          case 0:
            return CupertinoTabView(
              defaultTitle: SummaryPage.title,
              builder: (context) => SummaryPage(),
            );
          case 1:
            return CupertinoTabView(
              defaultTitle: PortfolioPage.title,
              builder: (context) => PortfolioPage(),
            );
          case 2:
            return CupertinoTabView(
                defaultTitle: AddPage.title, builder: (context) => AddPage());
          case 3:
            return CupertinoTabView(
              defaultTitle: ExtractPage.title,
              builder: (context) => ExtractPage(),
            );
          case 4:
            return CupertinoTabView(
              defaultTitle: AccountPage.title,
              builder: (context) => AccountPage(),
            );
          default:
            assert(false, 'Unexpected tab');
            return null;
        }
      },
    );
  }
}
