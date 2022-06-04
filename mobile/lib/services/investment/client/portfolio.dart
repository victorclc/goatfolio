import 'dart:convert';
import 'dart:io';

import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/investment/model/investment.dart';
import 'package:goatfolio/services/investment/model/investment_request.dart';
import 'package:goatfolio/services/investment/model/paginated_extract_result.dart';
import 'package:goatfolio/services/investment/model/paginated_investments_result.dart';
import 'package:goatfolio/services/investment/model/stock_dividend.dart';
import 'package:goatfolio/services/investment/model/stock_investment.dart';
import 'package:goatfolio/utils/logging_interceptor.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';
import 'package:intl/intl.dart';

class PortfolioClient {
  final UserService userService;
  final Client _client;

  PortfolioClient(this.userService)
      : _client = InterceptedClient.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<String> get accessToken async =>
      (await this.userService.getSessionToken())!;

  Future<PaginatedInvestmentResult> getInvestments(
      int limit, String? lastEvaluatedId, DateTime? lastEvaluatedDate,
      {String? ticker}) async {
    String url = F.baseUrl + "investments/v2/investments?limit=$limit";
    if (lastEvaluatedId != null && lastEvaluatedDate != null) {
      url +=
          "&last_evaluated_id=${lastEvaluatedId.replaceAll("#", "%23")}&last_evaluated_date=${DateFormat("yyyyMMdd").format(lastEvaluatedDate)}";
    }
    final Response response = await _client
        .get(Uri.parse(url), headers: {'Authorization': await accessToken});

    return PaginatedInvestmentResult.fromJson(jsonDecode(response.body));
  }

  Future<StockInvestment> addStockInvestment(StockInvestment investment) async {
    final request = InvestmentRequest(type: 'STOCK', investment: investment);
    final response = await _client.post(
      Uri.parse(F.baseUrl + "investments/investments/"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode != HttpStatus.ok) {
      throw Exception("Add Stock Investment failed");
    }
    return StockInvestment.fromJson(jsonDecode(response.body));
  }

  Future<void> editStockInvestment(StockInvestment investment) async {
    final request = InvestmentRequest(type: 'STOCK', investment: investment);
    final response = await _client.put(
      Uri.parse(F.baseUrl + "investments/investments/"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken,
      },
      body: jsonEncode(request.toJson()),
    );
    if (response.statusCode != HttpStatus.ok) {
      throw Exception("Edit Stock Investment failed");
    }
  }

  Future<void> delete(Investment investment) async {
    final response = await _client.delete(
      Uri.parse(F.baseUrl + "investments/investments/"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode({"investment_id": investment.id}),
    );
    if (response.statusCode != 200) {
      throw Exception("Delete failed");
    }
  }

  // Future<List<Investment>> getInvestmentsByTicker(String ticker) async {
  //   String url =
  //       F.baseUrl + "investments/v2/investments?ticker=${ticker.trim()}";
  //
  //   final Response response = await _client
  //       .get(Uri.parse(url), headers: {'Authorization': await accessToken});
  //
  //   return jsonDecode(response.body)
  //       .map<Investment?>(
  //         (investment) {
  //           if (investment["type"] == "STOCK") {
  //             return StockInvestment.fromJson(investment);
  //           } else if (investment["type"] == "STOCK_DIVIDEND") {
  //             return StockDividend.fromJson(investment);
  //           }
  //         },
  //       )
  //       .whereType<Investment>()
  //       .toList();
  // }

  Future<PaginatedExtractResult> getExtract(
      int limit, String? lastEvaluatedId, DateTime? lastEvaluatedDate) async {
    String url = F.baseUrl + "investments/bff/extract?limit=$limit";
    if (lastEvaluatedId != null && lastEvaluatedDate != null) {
      url +=
          "&last_evaluated_id=${lastEvaluatedId.replaceAll("#", "%23")}&last_evaluated_date=${DateFormat("yyyyMMdd").format(lastEvaluatedDate)}";
    }

    final Response response = await _client
        .get(Uri.parse(url), headers: {'Authorization': await accessToken});

    return PaginatedExtractResult.fromJson(jsonDecode(response.body));
  }

  Future<PaginatedExtractResult> getInvestmentsByTicker(
      String ticker) async {
    String url = F.baseUrl + "investments/bff/extract?ticker=${ticker.trim()}";

    final Response response = await _client
        .get(Uri.parse(url), headers: {'Authorization': await accessToken});

    return PaginatedExtractResult.fromJson(jsonDecode(response.body));
  }
}
