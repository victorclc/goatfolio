import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_list.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';

class PortfolioPerformanceNotifier
    with ChangeNotifier, DiagnosticableTreeMixin {
  final UserService userService;
  final PerformanceClient _client;
  Future<PortfolioPerformance> _future;
  Future<PortfolioSummary> _futureSummary;
  Future<PortfolioList> _futureList;

  PortfolioPerformanceNotifier(this.userService)
      : _client = PerformanceClient(userService) {
    // _future = _client.getPortfolioPerformance();
    _futureSummary = _client.getPortfolioSummary();
    _futureList = _client.getPortfolioPerformance();
  }

  get future => _future;
  get futureSummary => _futureSummary;
  get futureList => _futureList;

  void updatePerformance() async {
    // _future = _client.getPortfolioPerformance();
    // await _future;
    // TODO MUDAR ISSO URGENTEMENTE
    _futureList = _client.getPortfolioPerformance();
    _futureSummary = _client.getPortfolioSummary();
    await _futureSummary;
    await _futureList;

    notifyListeners();
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties.add(IntProperty('performance', future));
  }
}
