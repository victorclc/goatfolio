import 'package:flutter/material.dart';

class AppConfig extends InheritedWidget {
  AppConfig({
    @required this.cognitoUserPoolId,
    @required this.cognitoClientId,
    @required this.cognitoIdentityPoolId,
    @required Widget child,
  }) : super(child: child);

  final String cognitoUserPoolId;
  final String cognitoClientId;
  final String cognitoIdentityPoolId;

  static AppConfig of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType();
  }

  @override
  bool updateShouldNotify(InheritedWidget oldWidget) => false;
}
