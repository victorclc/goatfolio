import 'package:flutter/cupertino.dart';

class CupertinoThemeHelper {
  static Brightness currentBrightness(BuildContext context) {
    return CupertinoTheme.of(context).brightness ??
        MediaQuery.of(context).platformBrightness;
  }

  static bool isDarkMode(BuildContext context) {
    return CupertinoThemeHelper.currentBrightness(context) == Brightness.dark;
  }
}
