import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/investment/client/portfolio.dart';
import 'package:goatfolio/investment/model/stock.dart';
import 'package:goatfolio/investment/storage/stock_investment.dart';

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
}
