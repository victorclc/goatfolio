import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/stock/divergence_model.dart';
import 'package:goatfolio/services/stock/stock_client.dart';

enum DivergenceState { NO_DIVERGENCE, HAS_DIVERGENCE }

class StockDivergenceCubit extends Cubit<DivergenceState> {
  final UserService userService;
  late StockClient _client;

  List<Divergence> divergences = [];

  StockDivergenceCubit(this.userService)
      : super(DivergenceState.NO_DIVERGENCE) {
    _client = StockClient(userService);
  }

  void resolveDivergence(Divergence divergence, double averagePrice) async {
    final now = DateTime.now();
    final date = DateTime(now.year, now.month - 18, now.day);
    await _client.fixAveragePrice(
        divergence.ticker, date, '', divergence.missingAmount, averagePrice);
    divergences.remove(divergence);
    updateState();
  }

  Future<void> updateState() async {
    if (divergences.isNotEmpty) {
      emit(DivergenceState.HAS_DIVERGENCE);
    } else {
      emit(DivergenceState.NO_DIVERGENCE);
    }
  }

  Future<void> registerDivergences(List<Divergence> divergences) async {
    this.divergences = divergences;
    updateState();
  }

  Future<void> updateDivergences() async {
    await registerDivergences(await _client.getStockDivergences());
  }
}
