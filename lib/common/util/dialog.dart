import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class DialogUtils {
  static Future<void> showSuccessDialog(BuildContext context, String message,
      [String title = "Tudo certo!"]) async {
    return _cupertinoNotifyDialog(context, title, message);
  }

  static Future<void> showErrorDialog(BuildContext context, String message,
      [String title = "Erro"]) async {
    return _cupertinoNotifyDialog(context, title, message);
  }

  static Future<void> showNoYesDialog(BuildContext context,
      {String title,
      String message,
      Function onYesPressed,
      Function onNoPressed}) async {
    return _cupertinoNoYesDialog(context, title: title, message: message,
        onYesPressed: () async {
      if (onYesPressed != null) await onYesPressed();
      Navigator.of(context).pop();
    }, onNoPressed: () async {
      if (onNoPressed != null) {
        await onNoPressed();
      }
      Navigator.pop(context);
    });
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
        textStyle: TextStyle(color: Colors.red),
        onPressed: onYesPressed,
        child: Text("Excluir"),
      ),
    ]);
  }

  static Future<void> _cupertinoNotifyDialog(
      BuildContext context, String title, String message) async {
    await _cupertinoDialog(context, title, message, [
      CupertinoDialogAction(
        child: Text("OK"),
        isDefaultAction: true,
        onPressed: () => Navigator.pop(context),
      )
    ]);
  }

  static Future<void> _androidNotifyDialog(
      BuildContext context, String title, String message) async {
    await _androidDialog(context, title, message, [
      SimpleDialogOption(
          child: CupertinoButton(
        padding: EdgeInsets.zero,
        child: Text("OK"),
        onPressed: () => Navigator.of(context).pop(),
      )),
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

  static Future<void> _androidDialog(BuildContext context, String title,
      String message, List<Widget> actions) async {
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
}
