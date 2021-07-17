import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/common/http/interceptor/logging.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/vandelay/model/import_request.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';

class VandelayClient {
  final UserService userService;
  final Client _client;

  VandelayClient(this.userService) : _client = InterceptedClient.build(
      interceptors: [LoggingInterceptor()],
      requestTimeout: Duration(seconds: 30));


  Future<bool> importCEIRequest(String username, String password) async {
    CeiImportRequest request =
    CeiImportRequest(taxId: username, password: password);
    String accessToken = await userService.getSessionToken();

    var response = await _client.post(
      Uri.parse(F.baseUrl + "vandelay/cei/"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': accessToken
      },
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode != HttpStatus.accepted) {
      throw Exception("Import request failed");
    }
    return true;
  }
}