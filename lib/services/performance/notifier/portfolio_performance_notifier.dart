import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';

class PortfolioPerformanceNotifier
    with ChangeNotifier, DiagnosticableTreeMixin {
  final UserService userService;
  final PerformanceClient _client;
  Future<PortfolioPerformance> _future;

  PortfolioPerformanceNotifier(this.userService)
      : _client = PerformanceClient(userService) {
    _future = _client.getPortfolioPerformance();
  }

  get future => _future;

  void updatePerformance() async {
    _future = _client.getPortfolioPerformance();
    await _future;
    notifyListeners();
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties.add(IntProperty('performance', future));
  }
}
