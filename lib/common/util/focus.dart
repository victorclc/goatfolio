import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class FocusUtils {
  static void unfocus(BuildContext context) {
    FocusScopeNode currentFocus = FocusScope.of(context);
    if (!currentFocus.hasPrimaryFocus) {
      currentFocus.unfocus();
    }
  }
}
