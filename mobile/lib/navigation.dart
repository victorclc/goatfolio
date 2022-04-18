import 'dart:io';

import 'package:badges/badges.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/pages/add/add.dart';
import 'package:goatfolio/pages/extract/extract.dart';
import 'package:goatfolio/pages/portfolio/portfolio.dart';
import 'package:goatfolio/pages/settings/settings_page.dart';
import 'package:goatfolio/pages/summary/summary.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/notification/firebase.dart';
import 'package:goatfolio/services/stock/stock_divergence_cubit.dart';
import 'package:rate_my_app/rate_my_app.dart';

Widget buildNavigationPage(UserService userService) {
  //TODO VER ONDE POR ISSO
  setupPushNotifications(userService);
  return NavigationWidget();
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
  RateMyApp rateMyApp = RateMyApp(
    preferencesPrefix: 'rateMyApp_',
    minDays: 7,
    minLaunches: 7
  );

  late CupertinoTabController controller;
  int currentIndex = 0;
  late List<CupertinoTabView> iosTabViews;
  late List<Widget> androidTabViews;

  @override
  void initState() {
    super.initState();
    controller = new CupertinoTabController();
    if (Platform.isIOS) {
      initStateIos();
    } else {
      initStateAndroid();
    }

    WidgetsBinding.instance?.addPostFrameCallback((_) async {
      await rateMyApp.init();
      if (mounted && rateMyApp.shouldOpenDialog) {
        rateMyApp.showRateDialog(context,
            title: "Você está gostando do Goatfolio?",
            message:
                "Deixe sua avaliação e nos ajude a melhorar. Não vai demorar mais que um minuto.",
            rateButton: "AVALIAR",
            laterButton: "DEPOIS",
            noButton: "NÃO, OBRIGADO");
      }
    });
  }

  void initStateAndroid() {
    androidTabViews = [
      Builder(builder: (context) => SummaryPage()),
      Builder(builder: (context) => PortfolioPage()),
      Builder(builder: (context) => AddPage()),
      Builder(builder: (context) => ExtractPage()),
      Builder(builder: (context) => SettingsPage()),
    ];
  }

  void initStateIos() {
    iosTabViews = [
      CupertinoTabView(
        defaultTitle: SummaryPage.title,
        builder: (context) => SummaryPage(),
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
  Widget build(BuildContext context) {
    if (Platform.isIOS) {
      return buildIos(context);
    } else {
      return buildAndroid(context);
    }
  }

  Widget buildAndroid(BuildContext context) {
    final theme = CupertinoTheme.of(context);
    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: IndexedStack(
        index: currentIndex,
        children: androidTabViews,
      ),
      bottomNavigationBar: BottomNavigationBar(
        // type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
        selectedItemColor: theme.primaryColor,
        unselectedItemColor: Colors.grey,
        onTap: (index) {
          setState(() {
            currentIndex = index;
          });
        },
        currentIndex: currentIndex,
        items: [
          BottomNavigationBarItem(
              backgroundColor: theme.barBackgroundColor,
              label: SummaryPage.title,
              icon: SummaryPage.icon),
          BottomNavigationBarItem(
            backgroundColor: theme.barBackgroundColor,
            label: PortfolioPage.title,
            icon: PortfolioPage.icon,
          ),
          BottomNavigationBarItem(
            backgroundColor: theme.barBackgroundColor,
            label: AddPage.title,
            icon: BlocBuilder<StockDivergenceCubit, DivergenceState>(
                builder: (context, state) {
              return Badge(
                padding: state == DivergenceState.HAS_DIVERGENCE
                    ? EdgeInsets.all(5)
                    : EdgeInsets.zero,
                position: BadgePosition.topEnd(top: -2, end: -4),
                child: AddPage.icon,
              );
            }),
          ),
          BottomNavigationBarItem(
            backgroundColor: theme.barBackgroundColor,
            label: ExtractPage.title,
            icon: ExtractPage.icon,
          ),
          BottomNavigationBarItem(
            backgroundColor: theme.barBackgroundColor,
            label: SettingsPage.title,
            icon: SettingsPage.icon,
          ),
        ],
      ),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoTabScaffold(
      controller: controller,
      resizeToAvoidBottomInset: false,
      tabBar: CupertinoTabBar(
        onTap: (index) {
          if (index == currentIndex) {
            Navigator.of(iosTabViews[index].navigatorKey!.currentContext!)
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
            label: AddPage.title,
            icon: BlocBuilder<StockDivergenceCubit, DivergenceState>(
                builder: (context, state) {
              return Badge(
                padding: state == DivergenceState.HAS_DIVERGENCE
                    ? EdgeInsets.all(5)
                    : EdgeInsets.zero,
                position: BadgePosition.topEnd(top: -2, end: -4),
                child: AddPage.icon,
              );
            }),
          ),
          BottomNavigationBarItem(
              label: ExtractPage.title, icon: ExtractPage.icon),
          BottomNavigationBarItem(
              label: SettingsPage.title, icon: SettingsPage.icon),
        ],
      ),
      tabBuilder: (context, index) {
        switch (index) {
          case 0:
            return iosTabViews[0];
          case 1:
            return iosTabViews[1];
          case 2:
            return iosTabViews[2];
          case 3:
            return iosTabViews[3];
          case 4:
            return iosTabViews[4];
          default:
            assert(false, 'Unexpected tab');
            return Container();
        }
      },
    );
  }
}
