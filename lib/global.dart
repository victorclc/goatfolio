import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/pages/login/cubit/authentication_cubit.dart';

List<BlocProvider> buildGlobalProviders() {
  return [
      BlocProvider<AuthenticationCubit>(
    create: (_) => AuthenticationCubit(),
  ),
  ];
}

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