import 'dart:convert';
import 'package:goatfolio/common/http/interceptor/logging.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:goatfolio/services/performance/model/portfolio_list.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:goatfolio/services/performance/model/ticker_consolidated_history.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';

class PerformanceClient {
  final UserService userService;
  final Client _client;

  PerformanceClient(this.userService)
      : _client = InterceptedClient.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<PortfolioList> getPortfolioPerformance() async {
    String accessToken = await userService.getSessionToken();
    String url = F.baseUrl + "performance/portfolio";
    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': accessToken});

    return PortfolioList.fromJson(jsonDecode(response.body));
  }

  Future<PortfolioSummary> getPortfolioSummary() async {
    String accessToken = await userService.getSessionToken();
    String url = F.baseUrl + "performance/summary";
    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': accessToken});

    return PortfolioSummary.fromJson(jsonDecode(response.body));
  }

  Future<PortfolioHistory> getPortfolioRentabilityHistory() async {
    String accessToken = await userService.getSessionToken();
    String url = F.baseUrl + "performance/rentability";
    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': accessToken});

    return PortfolioHistory.fromJson(jsonDecode(response.body));
  }

  Future<TickerConsolidatedHistory> getTickerConsolidatedHistory(
      String ticker, String aliasTicker) async {
    String accessToken = await userService.getSessionToken();
    String url = F.baseUrl + "performance/ticker?ticker=$ticker";
    if (aliasTicker != null && aliasTicker.isNotEmpty) {
      url += '&alias_ticker=$aliasTicker';
    }
    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': accessToken});

    return TickerConsolidatedHistory.fromJson(jsonDecode(response.body));
  }
}
