import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/client/client.dart';
import 'package:goatfolio/services/friends/model/friend_rentability.dart';

class FriendsRentabilityCubit extends Cubit<LoadingState> {
  final FriendsClient _client;
  List<FriendRentability>? rentabilityList;

  FriendsRentabilityCubit(UserService userService)
      : _client = FriendsClient(userService),
        super(LoadingState.LOADING) {
    refresh();
  }

  Future<void> refresh() async {
    emit(LoadingState.LOADING);
    try {
      final list = await _client.getFriendsRentability();
      rentabilityList = list;
      emit(LoadingState.LOADED);
    } on Exception catch (e) {
      if (rentabilityList == null) emit(LoadingState.ERROR);
    }
  }
}
