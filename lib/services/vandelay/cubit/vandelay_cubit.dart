import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';

enum PendencyState { NO_PENDENCY, HAS_PENDENCY }

class VandelayPendencyCubit extends Cubit<PendencyState> {
  final UserService userService;
  List divergences = [];

  VandelayPendencyCubit(this.userService) : super(PendencyState.NO_PENDENCY);

  void registerAmountDivergence(String ticker, double amountMissing) {
    divergences.add({'ticker': ticker, 'amountMissing': amountMissing});
    emit(PendencyState.HAS_PENDENCY);
  }
}
