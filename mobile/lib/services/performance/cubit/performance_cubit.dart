import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';

class PerformanceCubit extends Cubit<LoadingState> {
  final PerformanceClient _client;
  PortfolioPerformance? portfolioPerformance;

  PerformanceCubit(UserService userService)
      : _client = PerformanceClient(userService),
        super(LoadingState.LOADING) {
    refresh();
  }

  Future<void> refresh() async {
    emit(LoadingState.LOADING);
    // try {
    final performance = await _client.getPortfolioPerformance();

    if (portfolioPerformance != null) {
      portfolioPerformance!.copy(performance);
    } else {
      portfolioPerformance = performance;
    }
    emit(LoadingState.LOADED);
    // }
    // catch (e) {
    //   if (portfolioPerformance == null) {
    //     emit(LoadingState.ERROR);
    //   }

    // }
  }
}
