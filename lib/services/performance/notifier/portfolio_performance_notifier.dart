import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_list.dart';

class PortfolioListNotifier with ChangeNotifier, DiagnosticableTreeMixin {
  final UserService userService;
  final PerformanceClient _client;
  Future<PortfolioList> _futureList;

  PortfolioListNotifier(this.userService)
      : _client = PerformanceClient(userService) {
    _futureList = _client.getPortfolioPerformance();
  }

  get futureList => _futureList;

  void updatePerformance() async {
    final tmpPerformance = _client.getPortfolioPerformance();
    var oldPerformance;
    try {
      oldPerformance = await _futureList;
    } catch (Exception) {}

    if (oldPerformance is PortfolioList) {
      tmpPerformance.then((value) {
        oldPerformance.copy(value);
      });
    } else {
      _futureList = tmpPerformance;
    }
    await tmpPerformance;
    notifyListeners();
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties.add(IntProperty('futureList', futureList));
  }
}
