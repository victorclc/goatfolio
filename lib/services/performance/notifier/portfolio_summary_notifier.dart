import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';

class PortfolioSummaryNotifier
    with ChangeNotifier, DiagnosticableTreeMixin {
  final UserService userService;
  final PerformanceClient _client;
  Future<PortfolioSummary> _futureSummary;

  PortfolioSummaryNotifier(this.userService)
      : _client = PerformanceClient(userService) {
    _futureSummary = _client.getPortfolioSummary();
  }

  get futureSummary => _futureSummary;

  void updatePerformance() async {
    final tmpSummary = _client.getPortfolioSummary();
    final oldSummary = await _futureSummary;

    tmpSummary.then((value) {
      oldSummary.copy(value);
      notifyListeners();
    });
    await tmpSummary;
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties.add(IntProperty('futureSummary', futureSummary));
  }
}
