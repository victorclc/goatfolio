

import 'package:goatfolio/authentication/cognito.dart';
import 'package:goatfolio/vandelay/client/client.dart';
import 'package:goatfolio/vandelay/storage/import_history.dart';

class VandelayService {
  final UserService userService;
  final ImportHistoryStorage storage;
  final VandelayClient client;

  VandelayService(this.userService)
      : storage = ImportHistoryStorage(),
        client = VandelayClient(userService);

  Future<void> importCEIRequest(String username, String password) async {
    final importResponse = await client.importCEIRequest(username, password);
    await storage.insert(importResponse.datetime, importResponse.status);
  }

// Future<void> editInvestment(StockInvestment investment) async {
//   await portfolioClient.editStockInvestment(investment);
//   await storage.insert(investment);
// }
//
// Future<void> deleteInvestment(StockInvestment investment) async {
//   await portfolioClient.delete(investment);
//   await storage.delete(investment);
// }
}
