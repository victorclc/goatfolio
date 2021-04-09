import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';

class PortfolioPerformanceNotifier
    with ChangeNotifier, DiagnosticableTreeMixin {
  final UserService userService;
  final PerformanceClient _client;
  Future<PortfolioPerformance> _future;
  Future<PortfolioSummary> _futureSummary;

  PortfolioPerformanceNotifier(this.userService)
      : _client = PerformanceClient(userService) {
    // _future = _client.getPortfolioPerformance();
    _futureSummary = _client.getPortfolioSummary();
  }

  get future => _future;
  get futureSummary => _futureSummary;

  void updatePerformance() async {
    // _future = _client.getPortfolioPerformance();
    // await _future;
    _futureSummary = _client.getPortfolioSummary();
    await _futureSummary;
    notifyListeners();
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties.add(IntProperty('performance', future));
  }
}
