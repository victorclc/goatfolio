import 'package:flutter/cupertino.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/client/client.dart';
import 'package:goatfolio/services/friends/model/friend.dart';
import 'package:goatfolio/services/friends/model/friends_list.dart';
import 'package:goatfolio/utils/dialog.dart';

class FriendsListCubit extends Cubit<LoadingState> {
  final FriendsClient _client;
  FriendsList? friendsList;

  FriendsListCubit(UserService userService)
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

  Future<void> cancel(BuildContext context, Friend friend) async {
    try {
      final message = await _client.cancelFriendRequest(friend.user);
      showSuccessDialog(context, message);
      emit(LoadingState.LOADING);
      friendsList!.invites.remove(friend);
      emit(LoadingState.LOADED);
    } on Exception catch (e) {
      showErrorDialog(
        context,
        e.toString().replaceAll("Exception: ", ""),
      );
    }
  }

  Future<String> add(String email) async {
    final message = await _client.addFriendRequest(email);
    return message;
  }

  Future<void> accept(BuildContext context, Friend friend) async {
    try {
      final message = await _client.acceptFriendRequest(friend.user);
      showSuccessDialog(context, message);
      emit(LoadingState.LOADING);
      friendsList!.requests.remove(friend);
      friendsList!.friends.add(friend);
      emit(LoadingState.LOADED);
    } on Exception catch (e) {
      showErrorDialog(
        context,
        e.toString().replaceAll("Exception: ", ""),
      );
    }
  }

  Future<void> decline(BuildContext context, Friend friend) async {
    try {
      final message = await _client.declineFriendRequest(friend.user);
      showSuccessDialog(context, message);
      emit(LoadingState.LOADING);
      friendsList!.requests.remove(friend);
      emit(LoadingState.LOADED);
    } on Exception catch (e) {
      showErrorDialog(
        context,
        e.toString().replaceAll("Exception: ", ""),
      );
    }
  }

  Future<void> remove(BuildContext context, Friend friend) async {
    try {
      final message = await _client.removeFriend(friend.user);
      await showSuccessDialog(context, message);
      emit(LoadingState.LOADING);
      friendsList!.friends.remove(friend);
      emit(LoadingState.LOADED);
      Navigator.of(context).pop();
    } on Exception catch (e) {
      showErrorDialog(
        context,
        e.toString().replaceAll("Exception: ", ""),
      );
    }
  }
}
