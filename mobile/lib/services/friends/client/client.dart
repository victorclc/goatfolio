import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/model/friends_list.dart';
import 'package:goatfolio/services/help/model/faq.dart';
import 'package:goatfolio/services/help/model/faq_topic.dart';
import 'package:goatfolio/utils/logging_interceptor.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';

class FriendsClient {
  final UserService userService;
  final Client _client;

  FriendsClient(this.userService)
      : _client = InterceptedClient.build(
      interceptors: [LoggingInterceptor()],
      requestTimeout: Duration(seconds: 30));

  Future<String> get accessToken async =>
      (await this.userService.getSessionToken())!;



  Future<FriendsList> getFriendsLIst() async {
    final response = await _client.get(
      Uri.parse(F.baseUrl + "friends/list"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
    );

    if (response.statusCode == HttpStatus.ok) {
      return FriendsList.fromJson(jsonDecode(response.body));
    }
    throw Exception("Erro ao buscar lista de compartilhamento.");
  }
}
