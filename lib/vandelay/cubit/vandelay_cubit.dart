import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/authentication/cognito.dart';
import 'package:goatfolio/vandelay/client/client.dart';
import 'package:goatfolio/vandelay/storage/divergences_storage.dart';

enum PendencyState { NO_PENDENCY, HAS_PENDENCY }

class VandelayPendencyCubit extends Cubit<PendencyState> {
  DivergenceStorage _storage = DivergenceStorage();
  final UserService userService;
  late VandelayClient _client;

  Map<String, int> divergences = {};

  VandelayPendencyCubit(this.userService) : super(PendencyState.NO_PENDENCY) {
    updateDivergences();
    _client = VandelayClient(userService);
  }

  void resolvePendency(String ticker, double averagePrice) async {
    final now = DateTime.now();
    final date = DateTime(now.year, now.month - 18, now.day);
    await _client.fixAveragePrice(
        ticker, date, 'Inter', divergences[ticker]!.toDouble(), averagePrice);

    _storage.delete(ticker);
    updateDivergences();
  }

  Future<void> updateDivergences() async {
    await _storage.getAll().then((value) {
      divergences = {};
      value.forEach((element) {
        divergences[element.keys.first] = element.values.first;
      });
      print(divergences);
      if (divergences.isNotEmpty) {
        emit(PendencyState.HAS_PENDENCY);
      } else {
        emit(PendencyState.NO_PENDENCY);
      }
    });
  }

  void noAmountDivergence() {
    divergences.clear();
    _storage.deleteAll();
    emit(PendencyState.NO_PENDENCY);
  }

  Future<void> registerAmountDivergence(
      String ticker, double amountMissing) async {
    await _storage.insert(ticker, amountMissing.toInt());
    await updateDivergences();
    emit(PendencyState.HAS_PENDENCY);
  }
}
