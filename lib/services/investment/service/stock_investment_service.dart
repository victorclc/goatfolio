import 'package:flutter/cupertino.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/client/portfolio.dart';
import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/storage/stock_investment.dart';

class StockInvestmentService {
  final UserService userService;
  final StockInvestmentStorage storage;
  final PortfolioClient portfolioClient;

  StockInvestmentService(this.userService)
      : storage = StockInvestmentStorage(),
        portfolioClient = PortfolioClient(userService);

  Future<void> addInvestment(StockInvestment investment) async {
    final newInvestment = await portfolioClient.addStockInvestment(investment);
    await storage.insert(newInvestment);
  }

  Future<void> editInvestment(StockInvestment investment) async {
    await portfolioClient.editStockInvestment(investment);
    await storage.insert(investment);
  }

  Future<void> deleteInvestment(StockInvestment investment) async {
    await portfolioClient.delete(investment);
    await storage.delete(investment);
  }

  Future<List<StockInvestment>> getInvestments({int limit, int offset}) async {
    final data = await storage.getAll(limit, offset);

    if ((data == null || data.isEmpty) && offset == 0) {
      debugPrint("Buscando na API");
      List<StockInvestment> investments =
          await portfolioClient.getInvestments();
      investments.forEach((i) async => await storage.insert(i));
      return storage.getAll(limit, offset);
    }
    return data;
  }

  Future<void> refreshInvestments() async {
    debugPrint("Refreshing investments");
    List<StockInvestment> investments = await portfolioClient.getInvestments();
    await storage.deleteAll();
    investments.forEach((i) async => await storage.insert(i));
  }

  Future<List<StockInvestment>> getByTicker(String ticker) async {
    return storage.getByTicker(ticker);
  }
}
