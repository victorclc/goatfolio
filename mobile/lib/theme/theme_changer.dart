import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeChanger extends ChangeNotifier {
  static const String CFG_THEME_KEY = "cfgThemeKey";
  static const String CFG_AUTOMATIC_VALUE = 'AUTOMATIC';
  static const String CFG_LIGHT_VALUE = 'LIGHT';
  static const String CFG_DARK_VALUE = 'DARK';

  final SharedPreferences _prefs;
  late String? _configuredTheme;
  late CupertinoThemeData _themeData;
  late ThemeData _androidTheme;

  String? get configuredTheme => _configuredTheme;

  get themeData => _themeData;

  get androidTheme => _androidTheme;

  ThemeChanger(this._prefs) {
    _configuredTheme = this._prefs.get(CFG_THEME_KEY) as String?;
    _setConfiguredTheme();
  }

  void _setConfiguredTheme() {
    switch (configuredTheme) {
      case CFG_LIGHT_VALUE:
        _themeData = CupertinoThemeData.raw(
            Brightness.light, null, null, null, null, null);
        _androidTheme = ThemeData(
            brightness: Brightness.light,
            backgroundColor: CupertinoColors.lightBackgroundGray,
            scaffoldBackgroundColor: CupertinoColors.white);
        break;
      case CFG_DARK_VALUE:
        _themeData = CupertinoThemeData.raw(
            Brightness.dark, null, null, null, null, null);
        _androidTheme = ThemeData(
            brightness: Brightness.dark,
            backgroundColor: CupertinoColors.black,
            scaffoldBackgroundColor: CupertinoColors.black);
        break;
      default:
        _themeData = CupertinoThemeData();
        _androidTheme = ThemeData(
            brightness: Brightness.light,
            backgroundColor: CupertinoColors.lightBackgroundGray,
            scaffoldBackgroundColor: CupertinoColors.white);
        break;
    }
  }

  void setValue(String value) {
    _configuredTheme = value;
    _prefs.setString(CFG_THEME_KEY, _configuredTheme!);
    _setConfiguredTheme();
    notifyListeners();
  }

  ThemeData? get androidDarkThemeData {
    if (this.configuredTheme == null ||
        this.configuredTheme == ThemeChanger.CFG_AUTOMATIC_VALUE) {
      return ThemeData(
          brightness: Brightness.dark,
          backgroundColor: CupertinoColors.black,
          scaffoldBackgroundColor: CupertinoColors.black);
    }
    return null;
  }
}
