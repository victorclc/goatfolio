import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class DialogUtils {
  static Future<void> showSuccessDialog(BuildContext context, String message,
      [String title = "Tudo certo!"]) async {
    if (Platform.isIOS) {
      return _cupertinoNotifyDialog(context, title, message);
    } else {
      return _androidNotifyDialog(context, title, message);
    }
  }

  static Future<void> showErrorDialog(BuildContext context, String message,
      [String title = "Erro"]) async {
    if (Platform.isIOS) {
      return _cupertinoNotifyDialog(context, title, message);
    } else {
      return _androidNotifyDialog(context, title, message);
    }
  }

  static Future<void> showCustomErrorDialog(
      BuildContext context, Widget content,
      [String title = "Erro"]) async {
    if (Platform.isIOS) {
      return _cupertinoCustomNotifyDialog(context, title, content);
    } else {
      return _androidCustomNotifyDialog(context, title, content);
    }
  }

  static Future<void> showNoYesDialog(BuildContext context,
      {String title,
      String message,
      Function onYesPressed,
      Function onNoPressed}) async {
    if (Platform.isIOS) {
      return _cupertinoNoYesDialog(context, title: title, message: message,
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

  static Future<void> _cupertinoNoYesDialog(BuildContext context,
      {String title,
      String message,
      Function onYesPressed,
      Function onNoPressed}) async {
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

  static Future<void> _androidNoYesDialog(BuildContext context,
      {String title,
      String message,
      Function onYesPressed,
      Function onNoPressed}) async {
    await _androidDialog(context, title, message, [
      SimpleDialogOption(
          child: CupertinoButton(
        padding: EdgeInsets.zero,
        child: Text("Cancelar"),
        onPressed: onNoPressed,
      )),
      SimpleDialogOption(
          child: CupertinoButton(
        padding: EdgeInsets.zero,
        child: Text(
          "Excluir",
          style: TextStyle(color: Colors.red),
        ),
        onPressed: onYesPressed,
      )),
    ]);
  }

  static Future<void> _cupertinoNotifyDialog(
      BuildContext context, String title, String message) async {
    await _cupertinoDialog(context, title, message, [
      CupertinoDialogAction(
        child: Text("OK"),
        isDefaultAction: true,
        onPressed: () => Navigator.pop(context),
      ),
    ]);
  }

  static Future<void> _cupertinoCustomNotifyDialog(
      BuildContext context, String title, Widget content) async {
    await _cupertinoCustomDialog(context, title, content, [
      CupertinoDialogAction(
        child: Text("OK"),
        isDefaultAction: true,
        onPressed: () => Navigator.pop(context),
      )
    ]);
  }

  static Future<void> _androidCustomNotifyDialog(
      BuildContext context, String title, Widget content) async {
    await _androidCustomDialog(context, title, content, [
      SimpleDialogOption(
          child: CupertinoButton(
        padding: EdgeInsets.zero,
        child: Text("OK"),
        onPressed: () => Navigator.of(context).pop(),
      )),
    ]);
  }

  static Future<void> _androidNotifyDialog(
      BuildContext context, String title, String message) async {
    return _androidDialog(context, title, message, [
      SimpleDialogOption(
        child: CupertinoButton(
          padding: EdgeInsets.zero,
          child: Text("OK"),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
    ]);
  }

  static Future<void> _cupertinoDialog(BuildContext context, String title,
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

  static Future<void> _cupertinoCustomDialog(BuildContext context, String title,
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

  static Future<void> _androidCustomDialog(BuildContext context, String title,
      Widget content, List<Widget> actions) async {
    await showDialog(
      useRootNavigator: false,
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          content:  content,
          actions: actions,
        );
      },
    );
  }

  static Future<void> _androidDialog(BuildContext context, String title,
      String message, List<Widget> actions) async {
    return showDialog<bool>(
      context: context,
      useRootNavigator: true,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          content: Text(message),
          actions: actions,
        );
      },
    ).then((value) => print("SAIU DO DIALOG"));
  }
}
