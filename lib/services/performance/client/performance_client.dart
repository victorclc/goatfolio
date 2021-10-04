import 'dart:convert';
import 'package:goatfolio/common/http/interceptor/logging.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
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

  Future<PortfolioPerformance> getPortfolioPerformance() async {
    String accessToken = await userService.getSessionToken();
    String url = F.baseUrl + "portfolio/summary/grouped";
    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': accessToken});

    return PortfolioPerformance.fromJson(jsonDecode(response.body));
  }

  Future<PortfolioSummary> getPortfolioSummary() async {
    String accessToken = await userService.getSessionToken();
    String url = F.baseUrl + "portfolio/summary";
    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': accessToken});

    return PortfolioSummary.fromJson(jsonDecode(response.body));
  }

  Future<PortfolioHistory> getPortfolioRentabilityHistory() async {
    String accessToken = await userService.getSessionToken();
    String url = F.baseUrl + "portfolio/history";
    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': accessToken});

    return PortfolioHistory.fromJson(jsonDecode(response.body));
  }

  Future<TickerConsolidatedHistory> getTickerConsolidatedHistory(
      String ticker) async {
    String accessToken = await userService.getSessionToken();
    String url = F.baseUrl + "portfolio/history/$ticker";

    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': accessToken});

    return TickerConsolidatedHistory.fromJson(jsonDecode(response.body));
  }
}
