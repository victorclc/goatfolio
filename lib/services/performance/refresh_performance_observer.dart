import 'package:flutter/cupertino.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/common/bloc/loading/loading_observer.dart';
import 'package:goatfolio/common/bloc/loading/loading_state.dart';

import 'cubit/performance_cubit.dart';

class RefreshPerformanceObserver extends LoadingStateObserver {
  @override
  Future<void> listen(BuildContext context, LoadingState state) async {
    if (state == LoadingState.LOADING) {
      final performanceCubit =
          BlocProvider.of<PerformanceCubit>(context, listen: false);
      await performanceCubit.refresh();
    }
  }
}
