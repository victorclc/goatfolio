import 'package:flutter/cupertino.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeChanger extends ChangeNotifier {
  static const String CFG_THEME_KEY = "cfgThemeKey";
  static const String CFG_AUTOMATIC_VALUE = 'AUTOMATIC';
  static const String CFG_LIGHT_VALUE = 'LIGHT';
  static const String CFG_DARK_VALUE = 'DARK';

  final SharedPreferences _prefs;
  String _configuredTheme;
  CupertinoThemeData _themeData;

  String get configuredTheme => _configuredTheme;

  get themeData => _themeData;

  ThemeChanger(this._prefs) {
    _configuredTheme = this._prefs.get(CFG_THEME_KEY);
    _setConfiguredTheme();
  }

  void _setConfiguredTheme() {
    switch (configuredTheme) {
      case CFG_LIGHT_VALUE:
        _themeData = CupertinoThemeData.raw(
            Brightness.light, null, null, null, null, null);
        break;
      case CFG_DARK_VALUE:
        _themeData = CupertinoThemeData.raw(
            Brightness.dark, null, null, null, null, null);
        break;
      default:
        _themeData = CupertinoThemeData();
        break;
    }
  }

  void setValue(String value) {
    _configuredTheme = value;
    _prefs.setString(CFG_THEME_KEY, _configuredTheme);
    _setConfiguredTheme();
    notifyListeners();
  }
}
