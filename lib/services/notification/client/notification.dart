import 'dart:convert';

import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/http/interceptor/logging.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/notification/model/register_token.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_client_with_interceptor.dart';

class NotificationClient {
  final String baseUrl = 'https://dev.victorclc.com.br/';
  final UserService userService;
  final Client _client;

  NotificationClient(this.userService)
      : _client = HttpClientWithInterceptor.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<void> registerToken(String token) async {
    String accessToken = await userService.getSessionToken();
    if (accessToken == null) return;
    final request = RegisterTokenRequest(token);

    final response = await _client.post(
      baseUrl + "notification/register",
      headers: {
        'Content-type': 'application/json',
        'Authorization': accessToken
      },
      body: jsonEncode(request.toJson()),
    );
    debugPrint('registerToken response statusCode: ${response.statusCode}');
  }
}
