import 'package:flutter/cupertino.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_observer.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/services/friends/cubit/friends_rentability_cubit.dart';

class RefreshFriendsRentabilityObserver extends LoadingStateObserver {
  @override
  Future<void> listen(BuildContext context, LoadingState state) async {
    if (state == LoadingState.LOADING) {
      final cubit =
          BlocProvider.of<FriendsRentabilityCubit>(context, listen: false);
      await cubit.refresh();
    }
  }
}
