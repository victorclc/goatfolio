import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/theme/theme_changer.dart';
import 'package:goatfolio/common/util/navigator.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

void goToThemePage(BuildContext context) {
  NavigatorUtils.push(
    context,
    (context) => ThemePage(),
  );
}

class ThemePage extends StatefulWidget {
  @override
  _ThemePageState createState() => _ThemePageState();
}

class _ThemePageState extends State<ThemePage> {
  bool automaticTheme = false;
  bool lightTheme = false;
  bool darkTheme = false;

  ThemeChanger themeChanger;

  @override
  void initState() {
    super.initState();
    themeChanger = Provider.of<ThemeChanger>(context, listen: false);

    switch (themeChanger.configuredTheme) {
      case ThemeChanger.CFG_DARK_VALUE:
        darkTheme = true;
        break;
      case ThemeChanger.CFG_LIGHT_VALUE:
        lightTheme = true;
        break;
      default:
        automaticTheme = true;
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
  }

  Widget buildAndroid(BuildContext context) {
    final textColor =
        CupertinoTheme.of(context).textTheme.navTitleTextStyle.color;
    return Scaffold(
      appBar: AppBar(
        leading: BackButton(
          color: textColor,
        ),
        title: Text(
          "Aparência",
          style: TextStyle(color: textColor),
        ),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: buildContent(context),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Aparência"),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    return SafeArea(
      child: SettingsList(
        sections: [
          SettingsSection(
            title: 'TEMA',
            tiles: [
              SettingsTile(
                title: 'Automático',
                trailing: automaticTheme
                    ? Icon(CupertinoIcons.check_mark, size: 18)
                    : Container(),
                onPressed: (_) {
                  setState(() {
                    automaticTheme = true;
                    lightTheme = false;
                    darkTheme = false;
                    themeChanger.setValue(ThemeChanger.CFG_AUTOMATIC_VALUE);
                  });
                },
              ),
              SettingsTile(
                title: 'Claro',
                trailing: lightTheme
                    ? Icon(CupertinoIcons.check_mark, size: 18)
                    : Container(),
                onPressed: (_) {
                  setState(() {
                    automaticTheme = false;
                    lightTheme = true;
                    darkTheme = false;
                    themeChanger.setValue(ThemeChanger.CFG_LIGHT_VALUE);
                  });
                },
              ),
              SettingsTile(
                title: 'Escuro',
                trailing: darkTheme
                    ? Icon(
                        CupertinoIcons.check_mark,
                        size: 18,
                      )
                    : Container(),
                onPressed: (_) {
                  setState(() {
                    automaticTheme = false;
                    lightTheme = false;
                    darkTheme = true;
                    themeChanger.setValue(ThemeChanger.CFG_DARK_VALUE);
                  });
                },
              ),
            ],
          )
        ],
      ),
    );
  }
}
