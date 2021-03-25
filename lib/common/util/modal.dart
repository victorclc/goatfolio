import 'package:flutter/cupertino.dart';
import 'package:modal_bottom_sheet/modal_bottom_sheet.dart';

class ModalUtils {
  static Future<T> showUnDismissibleModalBottomSheet<T>(
      BuildContext context, Widget child) async {
    return await showCupertinoModalBottomSheet(
        duration: Duration(milliseconds: 400),
        enableDrag: false,
        isDismissible: false,
        context: context,
        builder: (context) {
          return child;
        });
  }

  static Future<T> showDragableModalBottomSheet<T>(
      BuildContext context, Widget child,
      {bool expandable = true, bool isDismissible = false}) async {
    return await showCupertinoModalBottomSheet(
        enableDrag: true,
        isDismissible: isDismissible,
        useRootNavigator: true,
        expand: expandable,
        context: context,
        builder: (context) {
          return child;
        });
  }
}
