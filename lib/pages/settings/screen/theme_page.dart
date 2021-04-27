import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/helper/theme_helper.dart';
import 'package:goatfolio/common/theme/theme_changer.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

void goToThemePage(BuildContext context) {
  Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => ThemePage(),
    ),
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
    return CupertinoPageScaffold(
      backgroundColor:
          CupertinoThemeHelper.currentBrightness(context) == Brightness.light
              ? Color(0xFFEFEFF4)
              : CupertinoTheme.of(context).scaffoldBackgroundColor,
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Tema"),
      ),
      child: SafeArea(
        child: Container(
          width: double.infinity,
          padding:
              Platform.isIOS ? EdgeInsets.zero : const EdgeInsets.only(top: 16),
          child: Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  child: SettingsList(
                    shrinkWrap: true,
                    physics: NeverScrollableScrollPhysics(),
                    backgroundColor: Platform.isAndroid
                        ? CupertinoThemeHelper.currentBrightness(context) ==
                        Brightness.light
                        ? CupertinoTheme.of(context).scaffoldBackgroundColor
                        : Color.fromRGBO(28, 28, 30, 1)
                        : null,
                    sections: [
                      SettingsSection(
                        tiles: [
                          SettingsTile(
                            titleTextStyle: CupertinoTheme.of(context)
                                .textTheme
                                .textStyle
                                .copyWith(
                                    fontWeight: FontWeight.normal,
                                    fontSize: 16),
                            title: 'Automático',
                            // trailing: automaticTheme
                            //     ? Icon(CupertinoIcons.check_mark, size: 18)
                            //     : Container(),
                            onPressed: (_) {
                              setState(() {
                                automaticTheme = true;
                                lightTheme = false;
                                darkTheme = false;
                                themeChanger
                                    .setValue(ThemeChanger.CFG_AUTOMATIC_VALUE);
                              });
                            },
                          ),
                          SettingsTile(
                            titleTextStyle: CupertinoTheme.of(context)
                                .textTheme
                                .textStyle
                                .copyWith(
                                    fontWeight: FontWeight.normal,
                                    fontSize: 16),
                            title: 'Claro',
                            // trailing: lightTheme
                            //     ? Icon(CupertinoIcons.check_mark, size: 18)
                            //     : Container(),
                            onPressed: (_) {
                              setState(() {
                                automaticTheme = false;
                                lightTheme = true;
                                darkTheme = false;
                                themeChanger
                                    .setValue(ThemeChanger.CFG_LIGHT_VALUE);
                              });
                            },
                          ),
                          SettingsTile(
                            titleTextStyle: CupertinoTheme.of(context)
                                .textTheme
                                .textStyle
                                .copyWith(
                                    fontWeight: FontWeight.normal,
                                    fontSize: 16),
                            title: 'Escuro',
                            // trailing: darkTheme
                            //     ? Icon(
                            //         CupertinoIcons.check_mark,
                            //         size: 18,
                            //       )
                            //     : Container(),
                            onPressed: (_) {
                              setState(() {
                                automaticTheme = false;
                                lightTheme = false;
                                darkTheme = true;
                                themeChanger
                                    .setValue(ThemeChanger.CFG_DARK_VALUE);
                              });
                            },
                          ),

                          // SettingsTile.switchTile(
                          //   title: 'Modo Noturno Automático',
                          //   onToggle: (value) {
                          //     setState(() {
                          //       automaticDarkMode = value;
                          //
                          //       Provider.of<ThemeChanger>(context, listen: false)
                          //           .setBrightness(automaticDarkMode
                          //               ? Brightness.dark
                          //               : Brightness.light);
                          //     });
                          //   },
                          //   switchActiveColor: CupertinoColors.activeGreen,
                          //   switchValue: automaticDarkMode,
                          // )
                        ],
                      )
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
