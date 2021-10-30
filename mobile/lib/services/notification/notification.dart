import 'dart:convert';

import 'package:flutter/cupertino.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/notification/register_token.dart';
import 'package:goatfolio/services/notification/unregister_token.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';

class NotificationClient {
  final UserService userService;
  final Client _client;

  NotificationClient(this.userService)
      : _client = InterceptedClient.build(
            // interceptors: [LoggingInterceptor()],
            interceptors: [],
            requestTimeout: Duration(seconds: 30));

  Future<void> registerToken(String token, String oldToken) async {
    String? accessToken = await userService.getSessionToken();
    if (accessToken == null) return;
    final request = RegisterTokenRequest(token, oldToken);
    final response = await _client.post(
      Uri.parse(F.baseUrl + "notification/register"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': accessToken
      },
      body: jsonEncode(request.toJson()),
    );
    debugPrint('registerToken response statusCode: ${response.statusCode}');
  }

  Future<void> unregisterToken(String token) async {
    String? accessToken = await userService.getSessionToken();
    if (accessToken == null) return;
    final request = UnRegisterTokenRequest(token);

    final response = await _client.post(
      Uri.parse(F.baseUrl + "notification/unregister"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': accessToken
      },
      body: jsonEncode(request.toJson()),
    );
    debugPrint('registerToken response statusCode: ${response.statusCode}');
  }
}
