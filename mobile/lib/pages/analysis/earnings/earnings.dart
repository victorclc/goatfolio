

import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/pages/analysis/earnings/widgets/earnings_bar_chart.dart';
import 'package:goatfolio/services/performance/model/earnings_history.dart';

void goToEarningsPage(BuildContext context) {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => EarningsPage(),
    ),
  );
}


class EarningsPage extends StatefulWidget {
  const EarningsPage({Key? key}) : super(key: key);

  @override
  State<EarningsPage> createState() => _EarningsPageState();
}

class _EarningsPageState extends State<EarningsPage> {

  @override
  void initState() {

    super.initState();
  }
  @override
  Widget build(BuildContext context) {
    return SafeArea(child: EarningsBarChart(earningsHistory: EarningsHistory([]),),);
  }
}
