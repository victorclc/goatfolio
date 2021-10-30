import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/stock/divergence_model.dart';
import 'package:goatfolio/utils/logging_interceptor.dart';

import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';
import 'package:intl/intl.dart';

class StockClient {
  final UserService userService;
  final Client _client;

  StockClient(this.userService)
      : _client = InterceptedClient.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<String> get accessToken async =>
      (await this.userService.getSessionToken())!;

  Future<void> fixAveragePrice(String ticker, DateTime date, String broker,
      int amount, double averagePrice) async {
    final request = {
      'ticker': ticker,
      'date_from': DateFormat("yyyyMMdd").format(date),
      'broker': broker,
      'amount': amount,
      'average_price': averagePrice
    };

    var response = await _client.post(
      Uri.parse(F.baseUrl + "portfolio/stock/fix-average"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(request),
    );

    if (response.statusCode != HttpStatus.ok) {
      throw Exception("Fix average failed");
    }
  }

  Future<List<Divergence>> getStockDivergences() async {
    var response = await _client.get(
      Uri.parse(F.baseUrl + "portfolio/stock/divergences"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
    );

    if (response.statusCode != HttpStatus.ok) {
      throw Exception("Import request failed");
    }

    return jsonDecode(response.body)
        .map<Divergence>((json) => Divergence.fromJson(json))
        .toList();
  }
}
