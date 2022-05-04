import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/investment/client/portfolio.dart';
import 'package:goatfolio/services/investment/model/paginated_investments_result.dart';
import 'package:goatfolio/services/investment/model/stock.dart';

class StockInvestmentService {
  final UserService userService;
  final PortfolioClient portfolioClient;

  StockInvestmentService(this.userService)
      : portfolioClient = PortfolioClient(userService);

  Future<void> addInvestment(StockInvestment investment) async {
    final newInvestment = await portfolioClient.addStockInvestment(investment);
  }

  Future<void> editInvestment(StockInvestment investment) async {
    await portfolioClient.editStockInvestment(investment);
  }

  Future<void> deleteInvestment(StockInvestment investment) async {
    await portfolioClient.delete(investment);
  }

  Future<PaginatedInvestmentResult> getInvestments(
      {required int limit,
      String? lastEvaluatedId,
      DateTime? lastEvaluatedDate}) async {
    return await portfolioClient.getInvestments(
        limit, lastEvaluatedId, lastEvaluatedDate);
  }

  Future<List<StockInvestment>> getByTicker(String ticker) async {
    return await portfolioClient.getInvestmentsByTicker(ticker);
  }
}
