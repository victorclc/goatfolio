import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/investment/model/investment.dart';
import 'package:goatfolio/services/investment/model/stock_investment.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';

class ExtractLoaderCubit extends Cubit<LoadingState> {
  static const int limit = 15;
  String? lastEvaluatedId;
  DateTime? lastEvaluatedDate;
  bool hasFinished = false;

  final StockInvestmentService _service;
  List<Investment>? investments;

  ExtractLoaderCubit(UserService userService)
      : _service = StockInvestmentService(userService),
        super(LoadingState.LOADING) {
    refreshAll();
  }

  Future<List<Investment>?> getInvestments() async {
    final data = await _service.getInvestments(
        limit: limit,
        lastEvaluatedId: lastEvaluatedId,
        lastEvaluatedDate: lastEvaluatedDate);
    if (data != null) {
      lastEvaluatedId = data.lastEvaluatedId;
      lastEvaluatedDate = data.lastEvaluatedDate;
      if (lastEvaluatedId == null) {
        hasFinished = true;
      }
    }
    return data.investments;
  }

  Future<void> refreshAll() async {
    emit(LoadingState.LOADING);
    lastEvaluatedId = null;
    lastEvaluatedDate = null;
    hasFinished = false;

    final investmentsResponse = await getInvestments();
    if (investmentsResponse != null) {
      investments = investmentsResponse;
    }
    emit(LoadingState.LOADED);
  }

  Future<void> loadNext() async {
    if (hasFinished) return;
    emit(LoadingState.UPDATING);
    final data = await getInvestments();

    if (data != null) {
      investments!.addAll(data);
    }
    emit(LoadingState.LOADED);
  }

  Future<List<Investment>> geAllByTicker(String ticker) async {
return [];
  }

  void deleteStock(StockInvestment investment) async {
    emit(LoadingState.UPDATING);
    _service.deleteInvestment(investment);
    emit(LoadingState.LOADED);
    investments!.remove(investment);
    loadNext();
  }
}
