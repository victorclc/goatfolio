import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/authentication/cognito.dart';
import 'package:goatfolio/vandelay/storage/divergences_storage.dart';


enum PendencyState { NO_PENDENCY, HAS_PENDENCY }

class VandelayPendencyCubit extends Cubit<PendencyState> {
  DivergenceStorage _storage = DivergenceStorage();
  final UserService userService;

  Map<String, int> divergences = {};

  VandelayPendencyCubit(this.userService) : super(PendencyState.NO_PENDENCY) {
    updateDivergences();
  }

  void updateDivergences() {
    _storage.getAll().then((value) {
      value.forEach((element) {
        divergences[element.keys.first]= element.values.first;
      });
      print(divergences);
      if (divergences.isNotEmpty) {
        emit(PendencyState.HAS_PENDENCY);
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
    updateDivergences();
    emit(PendencyState.HAS_PENDENCY);
  }
}
