import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';



class SummaryCubit extends Cubit<LoadingState> {
  final PerformanceClient _client;
  PortfolioSummary? portfolioSummary;

  SummaryCubit(UserService userService)
      : _client = PerformanceClient(userService),
        super(LoadingState.LOADING) {
    refresh();
  }

  Future<void> refresh() async {
    emit(LoadingState.LOADING);
    try {
      final summary = await _client.getPortfolioSummary();

      if (portfolioSummary != null) {
        portfolioSummary!.copy(summary);
      } else {
        portfolioSummary = summary;
      }
    } catch (Exception) {
      if (portfolioSummary == null) {
        emit(LoadingState.ERROR);
      }
    }
    emit(LoadingState.LOADED);
  }
}
