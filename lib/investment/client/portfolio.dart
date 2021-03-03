import 'dart:convert';

import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/http/interceptor/logging.dart';
import 'package:goatfolio/investment/model/stock.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_client_with_interceptor.dart';

class PortfolioClient {
  final String baseUrl = 'https://dev.victorclc.com.br/';
  final UserService userService;
  final Client _client;

  PortfolioClient(this.userService)
      : _client = HttpClientWithInterceptor.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<List<StockInvestment>> getInvestments(
      [int date, String operand]) async {
    String accessToken = await userService.getSessionToken();
    String url = baseUrl + "portfolio/investments";
    if (date != null && operand != null) {
      url += "?date=$operand.$date";
    }
    final Response response =
        await _client.get(url, headers: {'Authorization': accessToken});

    var stockInvestments = jsonDecode(response.body)
        .map<StockInvestment>((json) => StockInvestment.fromJson(json))
        .toList();

    List<StockInvestment> result =
        new List<StockInvestment>.from(stockInvestments);
    return result;
  }

  Future<void> delete(StockInvestment investment) async {
    String accessToken = await userService.getSessionToken();
    final response = await _client.delete(
      baseUrl + "portfolio/investments/" + investment.id,
      headers: {
        'Content-type': 'application/json',
        'Authorization': accessToken
      },
    );
    if (response.statusCode != 200) {
      throw Exception("Delete failed");
    }
  }
}
