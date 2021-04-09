import 'dart:convert';
import 'package:goatfolio/common/http/interceptor/logging.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:goatfolio/services/performance/model/portfolio_list.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:goatfolio/services/performance/model/ticker_consolidated_history.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_client_with_interceptor.dart';

class PerformanceClient {
  final String baseUrl = 'https://dev.victorclc.com.br/';
  final UserService userService;
  final Client _client;

  PerformanceClient(this.userService)
      : _client = HttpClientWithInterceptor.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<PortfolioList> getPortfolioPerformance() async {
    String accessToken = await userService.getSessionToken();
    String url = baseUrl + "performance/portfolio";
    final Response response =
        await _client.get(url, headers: {'Authorization': accessToken});

    return PortfolioList.fromJson(jsonDecode(response.body));
  }

  Future<PortfolioSummary> getPortfolioSummary() async {
    String accessToken = await userService.getSessionToken();
    String url = baseUrl + "performance/summary";
    final Response response =
        await _client.get(url, headers: {'Authorization': accessToken});

    return PortfolioSummary.fromJson(jsonDecode(response.body));
  }

  Future<PortfolioHistory> getPortfolioRentabilityHistory() async {
    String accessToken = await userService.getSessionToken();
    String url = baseUrl + "performance/rentability";
    final Response response =
        await _client.get(url, headers: {'Authorization': accessToken});

    return PortfolioHistory.fromJson(jsonDecode(response.body));
  }

  Future<TickerConsolidatedHistory> getTickerConsolidatedHistory(
      String ticker) async {
    String accessToken = await userService.getSessionToken();
    String url = baseUrl + "performance/portfolio/$ticker";
    final Response response =
        await _client.get(url, headers: {'Authorization': accessToken});

    return TickerConsolidatedHistory.fromJson(jsonDecode(response.body));
  }
}
