import 'package:flutter/cupertino.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/common/bloc/loading/loading_observer.dart';
import 'package:goatfolio/common/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/cubit/performance_cubit.dart';
import 'package:goatfolio/services/vandelay/client/client.dart';
import 'package:goatfolio/services/vandelay/model/import_request.dart';
import 'package:goatfolio/services/vandelay/storage/import_history.dart';
import 'package:provider/provider.dart';

class VandelayRefreshObserver extends LoadingStateObserver {
  ImportHistoryStorage _storage = ImportHistoryStorage();

  @override
  Future<void> listen(BuildContext context, LoadingState state) async {
    if (state != LoadingState.LOADING) return;

    final userService = Provider.of<UserService>(context, listen: false);
    final client = VandelayClient(userService);
    final latest = await _storage.getLatest();

    // if (latest.status == 'PROCESSING') {
    //
    // }
    final response = await client.getImportStatus(latest.datetime);

    if (response.status == 'SUCCESS') {
      final info = await client.getCEIInfo();
      final performance =
          BlocProvider.of<PerformanceCubit>(context).portfolioPerformance;
      print(info);
      performance.allStocks.forEach((stockSummary) {
        if (info.containsKey(stockSummary.currentTickerName)) {
          int ceiAmount = info[stockSummary.currentTickerName].toInt();
          if (stockSummary.amount != ceiAmount) {
            print("${stockSummary.currentTickerName} TA DIVERGENTE");
          }
        }
      });
    }
  }
}
