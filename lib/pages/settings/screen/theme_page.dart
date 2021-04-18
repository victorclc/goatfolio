import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/theme/theme_changer.dart';
import 'package:package_info/package_info.dart';
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
  bool automaticTheme = true;
  bool lightTheme = false;
  bool darkTheme = false;

  @override
  Widget build(BuildContext context) {
    final themeChanger = Provider.of<ThemeChanger>(context, listen: false);

    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
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
                  title: 'Automático',
                  trailing: automaticTheme
                      ? Icon(CupertinoIcons.check_mark, size: 18)
                      : Container(),
                  onPressed: (_) {
                    setState(() {
                      automaticTheme = true;
                      lightTheme = false;
                      darkTheme = false;
                      themeChanger.setTheme(CupertinoThemeData());
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
                      themeChanger.setBrightness(Brightness.light);
                    });
                  },
                ),
                SettingsTile(
                  title: 'Escuro',
                  trailing:
                      darkTheme ? Icon(CupertinoIcons.check_mark, size: 18,) : Container(),
                  onPressed: (_) {
                    setState(() {
                      automaticTheme = false;
                      lightTheme = false;
                      darkTheme = true;
                      themeChanger.setBrightness(Brightness.dark);
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
