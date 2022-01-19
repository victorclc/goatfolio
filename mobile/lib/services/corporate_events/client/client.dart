import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/corporate_events/model/group_event.dart';
import 'package:goatfolio/services/corporate_events/model/incorporation_event.dart';
import 'package:goatfolio/services/corporate_events/model/split_event.dart';
import 'package:goatfolio/utils/logging_interceptor.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';

class CorporateEventsClient {
  final UserService userService;
  final Client _client;

  CorporateEventsClient(this.userService)
      : _client = InterceptedClient.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<String> get accessToken async =>
      (await this.userService.getSessionToken())!;

  Future<String> addIncorporationEvent(IncorporationEvent event) async {
    final response = await _client.post(
      Uri.parse(F.baseUrl + "corporate-events/events/incorporation"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(event.toJson()),
    );

    if (response.statusCode == HttpStatus.badRequest) {
      throw Exception(jsonDecode(response.body)["message"] as String);
    }
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body)["message"] as String;
    }
    throw Exception("Erro ao adicionar evento, tente novamente mais tarde.");
  }

  Future<String> addGroupEvent(GroupEvent event) async {
    final response = await _client.post(
      Uri.parse(F.baseUrl + "corporate-events/events/group"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(event.toJson()),
    );

    if (response.statusCode == HttpStatus.badRequest) {
      throw Exception(jsonDecode(response.body)["message"] as String);
    }
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body)["message"] as String;
    }
    throw Exception("Erro ao adicionar evento, tente novamente mais tarde.");
  }

  Future<String> addSplitEvent(SplitEvent event) async {
    final response = await _client.post(
      Uri.parse(F.baseUrl + "corporate-events/events/split"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(event.toJson()),
    );

    if (response.statusCode == HttpStatus.badRequest) {
      throw Exception(jsonDecode(response.body)["message"] as String);
    }
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body)["message"] as String;
    }
    throw Exception("Erro ao adicionar evento, tente novamente mais tarde.");
  }
}
