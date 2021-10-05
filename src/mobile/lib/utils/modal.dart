import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:goatfolio/theme/theme_changer.dart';
import 'package:modal_bottom_sheet/modal_bottom_sheet.dart';
import 'package:provider/provider.dart';

Future<T> showUnDismissibleModalBottomSheet<T>(
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

Future<T> showDraggableModalBottomSheet<T>(BuildContext context, Widget child,
    {bool expandable = true, bool isDismissible = false}) async {
  if (Platform.isIOS) {
    return await showCupertinoModalBottomSheet(
        enableDrag: true,
        isDismissible: isDismissible,
        useRootNavigator: true,
        expand: expandable,
        context: context,
        builder: (context) {
          return child;
        });
  } else {
    return showAndroidDraggableModalBottomSheet(
      context,
      child,
      expandable: expandable,
      isDismissible: isDismissible,
    );
  }
}

Future<T> showAndroidDraggableModalBottomSheet<T>(
    BuildContext context, Widget child,
    {bool expandable = true, bool isDismissible = false}) async {
  return await showMaterialModalBottomSheet(
    context: context,
    builder: (_) => CupertinoTheme(
        data: Provider.of<ThemeChanger>(context, listen: false).themeData,
        child: child),
    expand: expandable,
    enableDrag: true,
    useRootNavigator: true,
    isDismissible: isDismissible,
  );
}
