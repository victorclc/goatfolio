import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/cubit/friends_list_cubit.dart';
import 'package:goatfolio/services/friends/cubit/friends_rentability_cubit.dart';
import 'package:goatfolio/services/friends/observer/refresh_friends_rentability_observer.dart';
import 'package:goatfolio/services/performance/cubit/performance_cubit.dart';
import 'package:goatfolio/services/performance/cubit/summary_cubit.dart';
import 'package:goatfolio/services/performance/observer/refresh_performance_observer.dart';
import 'package:goatfolio/services/stock/divergence_refresh_observer.dart';
import 'package:goatfolio/services/stock/stock_divergence_cubit.dart';

List<BlocProvider> buildGlobalProviders(UserService userService) {
  return [
    BlocProvider<SummaryCubit>(
      create: (_) => SummaryCubit(userService),
    ),
    BlocProvider<PerformanceCubit>(
      create: (_) => PerformanceCubit(userService),
    ),
    BlocProvider<StockDivergenceCubit>(
      create: (_) => StockDivergenceCubit(userService),
    ),
    BlocProvider<FriendsListCubit>(
      create: (_) => FriendsListCubit(userService),
      lazy: true,
    ),
    BlocProvider<FriendsRentabilityCubit>(
      create: (_) => FriendsRentabilityCubit(userService),
      lazy: true,
    ),
  ];
}

final loadingStateObservers = [
  RefreshPerformanceObserver(),
  DivergenceRefreshObserver()
];
