import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

Future<void> showSuccessDialog(BuildContext context, String message,
    [String title = "Tudo certo!"]) async {
  if (Platform.isIOS) {
    return _cupertinoNotifyDialog(context, title, message);
  } else {
    return _androidNotifyDialog(context, title, message);
  }
}

Future<void> showErrorDialog(BuildContext context, String message,
    [String title = "Erro"]) async {
  if (Platform.isIOS) {
    return _cupertinoNotifyDialog(context, title, message);
  } else {
    return _androidNotifyDialog(context, title, message);
  }
}

Future<void> showCustomErrorDialog(BuildContext context, Widget content,
    [String title = "Erro"]) async {
  if (Platform.isIOS) {
    return _cupertinoCustomNotifyDialog(context, title, content);
  } else {
    return _androidCustomNotifyDialog(context, title, content);
  }
}

Future<void> showNoYesDialog(BuildContext context,
    {required String title,
    required String message,
    Function? onYesPressed,
    Function? onNoPressed}) async {
  if (Platform.isIOS) {
    return cupertinoNoYesDialog(context, title: title, message: message,
        onYesPressed: () async {
      if (onYesPressed != null) onYesPressed();
      Navigator.of(context).pop();
    }, onNoPressed: () async {
      if (onNoPressed != null) {
        onNoPressed();
      }
      Navigator.pop(context);
    });
  } else {
    return _androidNoYesDialog(context, title: title, message: message,
        onYesPressed: () async {
      if (onYesPressed != null) onYesPressed();
      Navigator.of(context).pop();
    }, onNoPressed: () async {
      if (onNoPressed != null) {
        onNoPressed();
      }
      Navigator.pop(context);
    });
  }
}

Future<void> cupertinoNoYesDialog(BuildContext context,
    {required String title,
    required String message,
    void Function()? onYesPressed,
    void Function()? onNoPressed}) async {
  await _cupertinoDialog(context, title, message, [
    CupertinoDialogAction(
      isDefaultAction: true,
      child: Text("Cancelar"),
      onPressed: onNoPressed,
    ),
    CupertinoDialogAction(
      isDefaultAction: true,
      isDestructiveAction: true,
      textStyle: TextStyle(color: Colors.red),
      onPressed: onYesPressed,
      child: Text("Excluir"),
    ),
  ]);
}

Future<void> _androidNoYesDialog(BuildContext context,
    {required String title,
    required String message,
    void Function()? onYesPressed,
    void Function()? onNoPressed}) async {
  await _androidDialog(context, title, message, [
    SimpleDialogOption(
      onPressed: onNoPressed,
      child: Text("Cancelar"),
    ),
    SimpleDialogOption(
      onPressed: onYesPressed,
      child: Text(
        "Excluir",
        style: TextStyle(color: Colors.red),
      ),
    ),
  ]);
}

Future<void> _cupertinoNotifyDialog(
    BuildContext context, String title, String message) async {
  await _cupertinoDialog(context, title, message, [
    CupertinoDialogAction(
      child: Text("OK"),
      isDefaultAction: true,
      onPressed: () => Navigator.pop(context),
    )
  ]);
}

Future<void> _cupertinoCustomNotifyDialog(
    BuildContext context, String title, Widget content) async {
  await _cupertinoCustomDialog(context, title, content, [
    CupertinoDialogAction(
      child: Text("OK"),
      isDefaultAction: true,
      onPressed: () => Navigator.pop(context),
    )
  ]);
}

Future<void> _androidNotifyDialog(
    BuildContext context, String title, String message) async {
  await _androidDialog(context, title, message, [
    SimpleDialogOption(
      onPressed: () => Navigator.of(context).pop(),
      child: Text("OK"),
    ),
  ]);
}

Future<void> _androidCustomNotifyDialog(
    BuildContext context, String title, Widget content) async {
  await _androidCustomDialog(context, title, content, [
    SimpleDialogOption(
      onPressed: () => Navigator.of(context).pop(),
      child: Text("OK"),
    ),
  ]);
}

Future<void> _cupertinoDialog(BuildContext context, String title,
    String message, List<Widget> actions) async {
  await showCupertinoDialog(
    useRootNavigator: false,
    context: context,
    builder: (context) {
      return CupertinoAlertDialog(
        title: Text(title),
        content: Text(message),
        actions: actions,
      );
    },
  );
}

Future<void> _cupertinoCustomDialog(BuildContext context, String title,
    Widget content, List<Widget> actions) async {
  await showCupertinoDialog(
    useRootNavigator: false,
    context: context,
    builder: (context) {
      return CupertinoAlertDialog(
        title: Text(title),
        content: content,
        actions: actions,
      );
    },
  );
}

Future<void> _androidDialog(BuildContext context, String title, String message,
    List<Widget> actions) async {
  await showDialog(
    context: context,
    builder: (context) {
      return AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: actions,
      );
    },
  );
}

Future<void> _androidCustomDialog(BuildContext context, String title,
    Widget content, List<Widget> actions) async {
  await showDialog(
    context: context,
    builder: (context) {
      return AlertDialog(
        title: Text(title),
        content: content,
        actions: actions,
      );
    },
  );
}
