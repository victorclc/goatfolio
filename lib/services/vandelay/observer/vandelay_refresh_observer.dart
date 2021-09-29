import 'package:flutter/cupertino.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/common/bloc/loading/loading_observer.dart';
import 'package:goatfolio/common/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/cubit/performance_cubit.dart';
import 'package:goatfolio/services/vandelay/client/client.dart';
import 'package:goatfolio/services/vandelay/cubit/vandelay_cubit.dart';
import 'package:goatfolio/services/vandelay/storage/import_history.dart';
import 'package:provider/provider.dart';

class VandelayRefreshObserver extends LoadingStateObserver {
  ImportHistoryStorage _storage = ImportHistoryStorage();

  @override
  Future<void> listen(BuildContext context, LoadingState state) async {
    if (state != LoadingState.LOADING) return;
    final vandelay = BlocProvider.of<VandelayPendencyCubit>(context);
    final userService = Provider.of<UserService>(context, listen: false);
    final client = VandelayClient(userService);
    final latest = await _storage.getLatest();

    if (latest.status == 'PROCESSING') {
      final response = await client.getImportStatus(latest.datetime);
      await checkForDivergences(context, client, vandelay);
      if (response.status == 'SUCCESS') {
        _storage.updateStatus(latest.id, response.status);
      }
    } else if (vandelay.state == PendencyState.HAS_PENDENCY) {
      await checkForDivergences(context, client, vandelay);
    }
  }

  Future<void> checkForDivergences(BuildContext context, VandelayClient client,
      VandelayPendencyCubit vandelay) async {
    final info = await client.getCEIInfo();
    final performance =
        BlocProvider.of<PerformanceCubit>(context).portfolioPerformance;

    bool hasDivergence = false;
    performance.allStocks.forEach(
      (stockSummary) {
        if (info.containsKey(stockSummary.currentTickerName)) {
          int ceiAmount = info[stockSummary.currentTickerName].toInt();
          if (stockSummary.quantity != ceiAmount) {
            hasDivergence = true;
            print(
                'MISSING ${stockSummary.currentTickerName}\nCEI: $ceiAmount\nPortfolio: ${stockSummary.quantity}');
            vandelay.registerAmountDivergence(stockSummary.currentTickerName,
                ceiAmount - stockSummary.quantity);
          }
        }
      },
    );
    if (!hasDivergence) {
      vandelay.noAmountDivergence();
    }
  }
}
