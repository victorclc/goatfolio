import 'package:flutter/material.dart';
import 'package:goatfolio/common/bloc/loading/loading_state.dart';

abstract class LoadingStateObserver {
  Future<void> listen(BuildContext context, LoadingState state);
}
