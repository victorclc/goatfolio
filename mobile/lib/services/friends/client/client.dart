import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/model/friend_rentability.dart';
import 'package:goatfolio/services/friends/model/friends_list.dart';
import 'package:goatfolio/services/friends/model/user.dart';
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

  Future<FriendsList> getFriendsList() async {
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

  Future<String> addFriendRequest(String email) async {
    final response = await _client.post(
      Uri.parse(F.baseUrl + "friends/add"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode({"email": email}),
    );

    if (response.statusCode == HttpStatus.badRequest) {
      // TODO validar se eh bad request q retorna
      throw Exception(jsonDecode(response.body)["message"] as String);
    }
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body)["message"] as String;
    }
    throw Exception("Erro ao enviar convite, tente novamente mais tarde.");
  }

  Future<String> cancelFriendRequest(FriendUser user) async {
    final response = await _client.post(
      Uri.parse(F.baseUrl + "friends/cancel"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(user),
    );

    if (response.statusCode == HttpStatus.badRequest) {
      // TODO validar se eh bad request q retorna
      throw Exception(jsonDecode(response.body)["message"] as String);
    }
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body)["message"] as String;
    }
    throw Exception("Erro ao cancelar convite, tente novamente mais tarde.");
  }

  Future<String> acceptFriendRequest(FriendUser user) async {
    final response = await _client.post(
      Uri.parse(F.baseUrl + "friends/accept"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(user),
    );

    if (response.statusCode == HttpStatus.badRequest) {
      throw Exception(jsonDecode(response.body)["message"] as String);
    }
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body)["message"] as String;
    }
    throw Exception("Erro ao cancelar convite, tente novamente mais tarde.");
  }

  Future<String> declineFriendRequest(FriendUser user) async {
    final response = await _client.post(
      Uri.parse(F.baseUrl + "friends/decline"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(user),
    );

    if (response.statusCode == HttpStatus.badRequest) {
      throw Exception(jsonDecode(response.body)["message"] as String);
    }
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body)["message"] as String;
    }
    throw Exception("Erro ao cancelar convite, tente novamente mais tarde.");
  }

  Future<String> removeFriend(FriendUser user) async {
    final response = await _client.post(
      Uri.parse(F.baseUrl + "friends/remove"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(user),
    );

    if (response.statusCode == HttpStatus.badRequest) {
      throw Exception(jsonDecode(response.body)["message"] as String);
    }
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body)["message"] as String;
    }
    throw Exception(
        "Erro ao tentar remover amigo, tente novamente mais tarde.");
  }

  Future<List<FriendRentability>> getFriendsRentability() async {
    final response = await _client.get(
      Uri.parse(F.baseUrl + "friends/rentability"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
    );

    if (response.statusCode == HttpStatus.ok) {
      return (jsonDecode(response.body) as List<dynamic>)
          .map<FriendRentability>((json) => FriendRentability.fromJson(json))
          .toList();
    }
    throw Exception("Erro ao buscar dados de compartilhamento.");
  }
}
