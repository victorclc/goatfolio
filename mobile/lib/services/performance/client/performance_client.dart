import 'dart:convert';

import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/performance/model/earnings_history.dart';
import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:goatfolio/services/performance/model/ticker_consolidated_history.dart';
import 'package:goatfolio/utils/logging_interceptor.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';

class PerformanceClient {
  final UserService userService;
  final Client _client;

  PerformanceClient(this.userService)
      : _client = InterceptedClient.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<String> get accessToken async =>
      (await this.userService.getSessionToken())!;

  Future<PortfolioPerformance> getPortfolioPerformance() async {
    String url = F.baseUrl + "portfolio/summary/grouped";
    final Response response = await _client
        .get(Uri.parse(url), headers: {'Authorization': await accessToken});

    return PortfolioPerformance.fromJson(jsonDecode(response.body));
  }

  Future<PortfolioSummary> getPortfolioSummary() async {
    String url = F.baseUrl + "portfolio/summary";
    final Response response = await _client
        .get(Uri.parse(url), headers: {'Authorization': await accessToken});

    return PortfolioSummary.fromJson(jsonDecode(response.body));
  }

  Future<PortfolioHistory> getPortfolioRentabilityHistory() async {
    String url = F.baseUrl + "portfolio/history";
    final Response response = await _client
        .get(Uri.parse(url), headers: {'Authorization': await accessToken});

    return PortfolioHistory.fromJson(jsonDecode(response.body));
  }

  Future<TickerConsolidatedHistory> getTickerConsolidatedHistory(
      String ticker) async {
    String url = F.baseUrl + "portfolio/history/$ticker";

    final Response response = await _client
        .get(Uri.parse(url), headers: {'Authorization': await accessToken});

    return TickerConsolidatedHistory.fromJson(jsonDecode(response.body));
  }

  Future<EarningsHistory> getEarningsHistory() async {
    String url = F.baseUrl + "portfolio/cash-dividends";

    final Response response = await _client
        .get(Uri.parse(url), headers: {'Authorization': await accessToken});

    return EarningsHistory.fromJson(jsonDecode(response.body));
  }
}
