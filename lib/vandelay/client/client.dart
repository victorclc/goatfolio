import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/authentication/cognito.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/utils/logging_interceptor.dart';
import 'package:goatfolio/vandelay/model/import_request.dart';

import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';

class VandelayClient {
  final UserService userService;
  final Client _client;

  VandelayClient(this.userService)
      : _client = InterceptedClient.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<String> get accessToken async =>
      (await this.userService.getSessionToken())!;


  Future<CeiImportResponse> importCEIRequest(
      String username, String password) async {
    CeiImportRequest request =
        CeiImportRequest(taxId: username, password: password);

    var response = await _client.post(
      Uri.parse(F.baseUrl + "vandelay/cei/"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode != HttpStatus.accepted) {
      throw Exception("Import request failed");
    }
    return CeiImportResponse.fromJson(jsonDecode(response.body));
  }

  Future<Map<String, double>> getCEIInfo() async {
    final uri = Uri.parse(F.baseUrl + "vandelay/cei/info");

    var response = await _client.get(
      uri,
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
    );
    return Map<String, double>.from(jsonDecode(response.body));
  }

  Future<CeiImportResponse> getImportStatus(int datetime) async {
    final uri = Uri.parse(F.baseUrl + "vandelay/cei?datetime=$datetime");

    var response = await _client.get(
      uri,
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
    );
    if (response.statusCode != HttpStatus.ok) {
      throw Exception("Import status failed.");
    }
    return CeiImportResponse.fromJson(jsonDecode(response.body));
  }
}
