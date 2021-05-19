import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class NavigatorUtils {
  static Future<void> push(BuildContext context, Function builder) async {
    if (Platform.isIOS) {
      return await Navigator.push(
        context,
        CupertinoPageRoute(builder: builder),
      );
    } else {
      return await Navigator.push(
        context,
        MaterialPageRoute(builder: builder),
      );
    }
  }
}
