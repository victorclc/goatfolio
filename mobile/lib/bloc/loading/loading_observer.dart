import 'package:flutter/material.dart';

import 'loading_state.dart';

abstract class LoadingStateObserver {
  Future<void> listen(BuildContext context, LoadingState state);
}
