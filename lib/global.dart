import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/authentication/cognito.dart';
import 'package:goatfolio/performance/cubit/performance_cubit.dart';
import 'package:goatfolio/performance/cubit/summary_cubit.dart';
import 'package:goatfolio/vandelay/cubit/vandelay_cubit.dart';

List<BlocProvider> buildGlobalProviders(UserService userService) {
  return [
    BlocProvider<SummaryCubit>(
      create: (_) => SummaryCubit(userService),
    ),
    BlocProvider<PerformanceCubit>(
      create: (_) => PerformanceCubit(userService),
    ),
    BlocProvider<VandelayPendencyCubit>(
      create: (_) => VandelayPendencyCubit(userService),
    ),
  ];
}

const loadingStateObservers = [
  // RefreshPerformanceObserver(),
  // VandelayRefreshObserver()
];

// const globalProviders = [
//   BlocProvider<SummaryCubit>(
//     create: (_) => SummaryCubit(userService),
//   ),
//   BlocProvider<PerformanceCubit>(
//     create: (_) => PerformanceCubit(userService),
//   ),
//   BlocProvider<VandelayPendencyCubit>(
//     create: (_) => VandelayPendencyCubit(userService),
//   ),
// ];
