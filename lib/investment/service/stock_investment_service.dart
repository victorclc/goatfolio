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

  Future<void> deleteInvestment(StockInvestment investment) async {
    await portfolioClient.delete(investment);
    await storage.delete(investment);
  }
}
