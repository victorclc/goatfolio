import 'package:flutter/cupertino.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_observer.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/stock/stock_divergence_cubit.dart';

class DivergenceRefreshObserver extends LoadingStateObserver {
  @override
  Future<void> listen(BuildContext context, LoadingState state) async {
    if (state != LoadingState.LOADING) return;
    final cubit = BlocProvider.of<StockDivergenceCubit>(context);
    await cubit.updateDivergences();
  }
}
