import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/vandelay/storage/divergences_storage.dart';

enum PendencyState { NO_PENDENCY, HAS_PENDENCY }

class VandelayPendencyCubit extends Cubit<PendencyState> {
  DivergenceStorage _storage = DivergenceStorage();
  final UserService userService;

  List divergences = [];

  VandelayPendencyCubit(this.userService) : super(PendencyState.NO_PENDENCY) {
    _storage.getAll().then((value) {
      divergences = value;
      if (value.isNotEmpty) {
        emit(PendencyState.HAS_PENDENCY);
      }
    });
  }

  void noAmountDivergence() {
    divergences.clear();
    _storage.deleteAll();
    emit(PendencyState.NO_PENDENCY);
  }

  Future<void> registerAmountDivergence(String ticker, double amountMissing) async {
    await _storage.insert(ticker, amountMissing.toInt());
    divergences = await _storage.getAll();
    emit(PendencyState.HAS_PENDENCY);
  }
}
