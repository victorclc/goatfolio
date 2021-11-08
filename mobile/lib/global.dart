import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
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
  ];
}

final loadingStateObservers = [
  RefreshPerformanceObserver(),
  DivergenceRefreshObserver()
];
