import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/help/model/faq.dart';
import 'package:goatfolio/services/help/model/faq_topic.dart';
import 'package:goatfolio/utils/logging_interceptor.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';

class HelpClient {
  final UserService userService;
  final Client _client;

  HelpClient(this.userService)
      : _client = InterceptedClient.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<String> get accessToken async =>
      (await this.userService.getSessionToken())!;

  Future<Faq> getTopicFaq(FaqTopic topic) async {
    final response = await _client.get(
      Uri.parse(F.baseUrl + "help/faq?topic=${topic.toShortString()}"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
    );

    if (response.statusCode == HttpStatus.ok) {
      return Faq.fromJson(jsonDecode(response.body));
    }
    throw Exception("Erro ao buscar FAQ.");
  }

  Future<List<Faq>> getFaq() async {
    final response = await _client.get(
      Uri.parse(F.baseUrl + "help/faq"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
    );

    if (response.statusCode == HttpStatus.ok) {
      return (jsonDecode(response.body) as List)
          .map<Faq>((e) => Faq.fromJson(e))
          .toList();
    }
    throw Exception("Erro ao buscar FAQ.");
  }
}
