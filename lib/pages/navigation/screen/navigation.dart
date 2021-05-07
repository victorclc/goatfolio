import 'package:flutter/cupertino.dart';
import 'package:goatfolio/pages/add/screen/add.dart';
import 'package:goatfolio/pages/extract/extract.dart';
import 'package:goatfolio/pages/portfolio/screen/portfolio.dart';
import 'package:goatfolio/pages/settings/screen/settings_page.dart';
import 'package:goatfolio/pages/summary/screen/summary.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/notification/firebase/firebase.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_summary_notifier.dart';
import 'package:provider/provider.dart';

Widget buildNavigationPage(UserService userService) {
  setupPushNotifications(userService);
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

class _NavigationWidgetState extends State<NavigationWidget>
    with SingleTickerProviderStateMixin {
  CupertinoTabController controller;
  int currentIndex = 0;
  List<CupertinoTabView> tabViews;

  @override
  void initState() {
    super.initState();
    controller = new CupertinoTabController();

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
      tabBar: CupertinoTabBar(
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
          BottomNavigationBarItem(label: AddPage.title, icon: AddPage.icon),
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
