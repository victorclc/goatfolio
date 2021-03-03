import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/http/interceptor/logging.dart';
import 'package:goatfolio/vandelay/model/import_request.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_client_with_interceptor.dart';

class VandelayClient {
  final UserService userService;
  static final String baseUrl = 'https://dev.victorclc.com.br/';
  final Client _client;

  VandelayClient(this.userService) : _client = HttpClientWithInterceptor.build(
      interceptors: [LoggingInterceptor()],
      requestTimeout: Duration(seconds: 30));


  Future<void> importCEIRequest(String username, String password) async {
    CeiImportRequest request =
    CeiImportRequest(taxId: username, password: password);
    String accessToken = await userService.getSessionToken();

    var response = await _client.post(
      baseUrl + "vandelay/cei/",
      headers: {
        'Content-type': 'application/json',
        'Authorization': accessToken
      },
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode != HttpStatus.ok) {
      throw Exception("Import request failed");
    }
  }
}