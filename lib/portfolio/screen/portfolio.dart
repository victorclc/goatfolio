import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/performance/client/performance_client.dart';
import 'package:goatfolio/portfolio/widget/donut_chart.dart';
import 'package:provider/provider.dart';

import 'dart:math' as math;
import 'package:charts_flutter/flutter.dart' as charts;

class PortfolioPage extends StatefulWidget {
  static const title = 'Portfolio';
  static const icon = Icon(Icons.trending_up);

  @override
  _PortfolioPageState createState() => _PortfolioPageState();
}

class _PortfolioPageState extends State<PortfolioPage> {
  Map<String, Rgb> colors = Map();

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    final client = PerformanceClient(userService);
    client.getPerformance();
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoSliverPage(largeTitle: PortfolioPage.title, children: [
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            alignment: Alignment.centerLeft,
            padding: EdgeInsets.only(left: 16, bottom: 16, top: 8),
            child: Text(
              "Alocação",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          SizedBox(
              height: 240,
              width: double.infinity,
              child: DonutAutoLabelChart(buidInvestmentSeries()))
        ],
       ),
    ]);
  }

  List<charts.Series<TickerTotals, String>> buidInvestmentSeries() {
    List<TickerTotals> data = List();
    data.add(TickerTotals('BIDI11', 5000, Rgb.random()));
    data.add(TickerTotals('ITSA4', 2500, Rgb.random()));
    data.add(TickerTotals('WEGE3', 1250, Rgb.random()));
    data.add(TickerTotals('SQIA3', 1250, Rgb.random()));

    return [
      new charts.Series<TickerTotals, String>(
        id: 'investments',
        domainFn: (TickerTotals totals, _) => totals.ticker,
        measureFn: (TickerTotals totals, _) => totals.total,
        data: data,
        colorFn: (totals, _) => charts.Color(
            r: totals.color.r, g: totals.color.g, b: totals.color.b),
        // Set a label accessor to control the text of the arc label.
        labelAccessorFn: (TickerTotals totals, _) =>
            '${totals.ticker.replaceAll('.SA', '')}',
      )
    ];
  }
}

class TickerTotals {
  String ticker;
  double total;
  Rgb color;

  TickerTotals(this.ticker, this.total, this.color);
}

class Rgb {
  final int r;
  final int g;
  final int b;

  Rgb(this.r, this.g, this.b);

  Color toColor() {
    return Color.fromARGB(0xFF, this.r, this.g, this.b);
  }

  static Rgb random() {
    return Rgb(
        (math.Random().nextDouble() * 0xFF).toInt(),
        (math.Random().nextDouble() * 0xFF).toInt(),
        (math.Random().nextDouble() * 0xFF).toInt());
  }
}
