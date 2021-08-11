import 'package:flutter/cupertino.dart';

class CupertinoThemeHelper {
  static Brightness currentBrightness(BuildContext context) {
    return CupertinoTheme.of(context).brightness ??
        MediaQuery.of(context).platformBrightness;
  }
}
