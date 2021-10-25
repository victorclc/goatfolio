import 'dart:convert';
import 'dart:io';



import 'package:goatfolio/authentication/cognito.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/investment/model/investment_request.dart';
import 'package:goatfolio/investment/model/stock.dart';
import 'package:goatfolio/utils/logging_interceptor.dart';
import 'package:http/http.dart';
import 'package:http_interceptor/http_interceptor.dart';


class PortfolioClient {
  final UserService userService;
  final Client _client;

  PortfolioClient(this.userService)
      : _client = InterceptedClient.build(
            interceptors: [LoggingInterceptor()],
            requestTimeout: Duration(seconds: 30));

  Future<String> get accessToken async =>
      (await this.userService.getSessionToken())!;


  Future<List<StockInvestment>> getInvestments() async {
    String url = F.baseUrl + "investments/investments";
    final Response response =
        await _client.get(Uri.parse(url), headers: {'Authorization': await accessToken});

    var stockInvestments = jsonDecode(response.body)
        .map<StockInvestment>((json) => StockInvestment.fromJson(json))
        .toList();

    List<StockInvestment> result =
        new List<StockInvestment>.from(stockInvestments);
    return result;
  }

  Future<StockInvestment> addStockInvestment(StockInvestment investment) async {
    final request = InvestmentRequest(type: 'STOCK', investment: investment);
    final response = await _client.post(Uri.parse(
      F.baseUrl + "investments/investments/"),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
      body: jsonEncode(request.toJson()),
    );
    print("addStockInvestmentResponse: $response");

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

  Future<void> delete(StockInvestment investment) async {
    final response = await _client.delete(
      Uri.parse(F.baseUrl + "investments/investments/" + investment.id!),
      headers: {
        'Content-type': 'application/json',
        'Authorization': await accessToken
      },
    );
    if (response.statusCode != 200) {
      throw Exception("Delete failed");
    }
  }
}
