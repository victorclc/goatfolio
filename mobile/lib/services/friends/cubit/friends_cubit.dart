import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/client/client.dart';
import 'package:goatfolio/services/friends/model/friends_list.dart';

class FriendsCubit extends Cubit<LoadingState> {
  final FriendsClient _client;
  FriendsList? friendsList;

  FriendsCubit(UserService userService)
      : _client = FriendsClient(userService),
        super(LoadingState.LOADING) {
    refresh();
  }

  Future<void> refresh() async {
    emit(LoadingState.LOADING);
    try {
      final list = await _client.getFriendsList();
      friendsList = list;
      emit(LoadingState.LOADED);
    } on Exception catch (e) {
      if (friendsList == null) emit(LoadingState.ERROR);
    }
  }
}
