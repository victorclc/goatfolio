import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

void goToProgressIndicatorScaffold(BuildContext context, String message,
    Function onFinish, Future future) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => ProgressIndicatorScaffold(
        message: message,
        onFinish: onFinish,
        future: future,
      ),
    ),
  );
}

class ProgressIndicatorScaffold extends StatefulWidget {
  final String message;
  final Future future;
  final Function onFinish;

  const ProgressIndicatorScaffold(
      {Key? key, required this.message, required this.future, required this.onFinish})
      : super(key: key);

  @override
  _ProgressIndicatorScaffoldState createState() =>
      _ProgressIndicatorScaffoldState();
}

class _ProgressIndicatorScaffoldState extends State<ProgressIndicatorScaffold> {
  Future<void> onFinish() async {
    Navigator.of(context).pop();
    await widget.onFinish();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      future: widget.future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          onFinish();
        }
        return CupertinoPageScaffold(
          child: SafeArea(
            child: Center(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Platform.isIOS
                      ? CupertinoActivityIndicator()
                      : Center(child: CircularProgressIndicator()),
                  SizedBox(
                    height: 8,
                  ),
                  Text(
                    widget.message,
                    style: CupertinoTheme.of(context).textTheme.textStyle,
                  )
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
