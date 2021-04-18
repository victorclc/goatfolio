import 'package:flutter/cupertino.dart';

class ThemeChanger extends ChangeNotifier {
  CupertinoThemeData _themeData;

  ThemeChanger(this._themeData);

  get themeData => _themeData;

  void setBrightness(Brightness brightness) {
    _themeData =
        CupertinoThemeData.raw(brightness, null, null, null, null, null);
    notifyListeners();
  }

  void setTheme(CupertinoThemeData newTheme) {
    _themeData = newTheme;
    notifyListeners();
  }
}
