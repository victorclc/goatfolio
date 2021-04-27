import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
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
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Aparência"),
      ),
      child: SafeArea(
        child: SettingsList(
          sections: [
            SettingsSection(
              title: 'TEMA',
              tiles: [
                SettingsTile(
                  titleTextStyle: CupertinoTheme.of(context).textTheme.textStyle.copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                  title: 'Automático',
                  // trailing: automaticTheme
                  //     ? Icon(CupertinoIcons.check_mark, size: 18)
                  //     : Container(),
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
                  titleTextStyle: CupertinoTheme.of(context).textTheme.textStyle.copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                  title: 'Claro',
                  // trailing: lightTheme
                  //     ? Icon(CupertinoIcons.check_mark, size: 18)
                  //     : Container(),
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
                  titleTextStyle: CupertinoTheme.of(context).textTheme.textStyle.copyWith(fontWeight: FontWeight.normal, fontSize: 16),
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
                      themeChanger.setValue(ThemeChanger.CFG_DARK_VALUE);
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
    );
  }
}
