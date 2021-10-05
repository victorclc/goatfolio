import 'package:flutter/cupertino.dart';

Brightness currentBrightness(BuildContext context) {
  return CupertinoTheme.of(context).brightness ??
      MediaQuery.of(context).platformBrightness;
}

bool isDarkMode(BuildContext context) {
  return currentBrightness(context) == Brightness.dark;
}

bool isLightMode(BuildContext context) {
  return currentBrightness(context) != Brightness.dark;
}
