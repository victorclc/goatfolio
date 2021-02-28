import 'dart:convert';

import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/http/interceptor/logging.dart';
import 'package:goatfolio/investment/model/investment.dart';
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
            requestTimeout: Duration(seconds: 10));

  Future<List<Investment>> getInvestments() async {
    String accessToken = await userService.getSessionToken();
    final Response response = await _client.get(
        baseUrl + "portfolio/investments/",
        headers: {'Authorization': accessToken});

    var stockInvestments = jsonDecode(response.body)
        .where((i) => i['type'] == "STOCK")
        .map<StockInvestment>((json) => StockInvestment.fromJson(json))
        .toList();

    List<Investment> result = new List<Investment>.from(stockInvestments);
    return result;
  }
}
