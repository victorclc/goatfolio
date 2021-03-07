import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/performance/client/performance_client.dart';
import 'package:goatfolio/performance/model/monthly_performance.dart';
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
  Future<List<charts.Series<TickerTotals, String>>> _future;
  PerformanceClient client;
  List<StockMonthlyPerformance> performances;

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    client = PerformanceClient(userService);
    _future = getPerformanceSeries();
  }

  Future<List<charts.Series<TickerTotals, String>>>
      getPerformanceSeries() async {
    performances = await client.getPerformance();
    return await buildInvestmentSeries(performances);
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoSliverPage(largeTitle: PortfolioPage.title, children: [
      FutureBuilder(
        future: _future,
        builder: (context, snapshot) {
          switch (snapshot.connectionState) {
            case ConnectionState.none:
            case ConnectionState.active:
              break;
            case ConnectionState.waiting:
              return CupertinoActivityIndicator();
            case ConnectionState.done:
              print(
                  "Snapshot: $snapshot\nSnapshot.hastData: ${snapshot.hasData}");
              if (snapshot.hasData) {
                return Column(
                  children: [
                    Container(
                      alignment: Alignment.centerLeft,
                      padding: EdgeInsets.only(left: 16, bottom: 16, top: 8),
                      child: Text(
                        "Alocação",
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                    SizedBox(
                      height: 240,
                      width: double.infinity,
                      child: DonutAutoLabelChart(
                        snapshot.data,
                      ),
                    ),
                    Container(
                      padding: EdgeInsets.only(left: 16, right: 16),
                      child: ListView.builder(
                        padding: EdgeInsets.zero,
                        physics: NeverScrollableScrollPhysics(),
                        shrinkWrap: true,
                        itemCount: performances.length,
                        itemBuilder: (context, index) {
                          return Text(performances[index].ticker);
                        },
                      ),
                    ),
                  ],
                );
              }
          }
          return Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                height: 32,
              ),
              Text("Tivemos um problema ao carregar",
                  style: Theme.of(context).textTheme.subtitle1),
              Text(" as informações.",
                  style: Theme.of(context).textTheme.subtitle1),
              SizedBox(
                height: 8,
              ),
              Text("Toque para tentar novamente.",
                  style: Theme.of(context).textTheme.subtitle1),
              CupertinoButton(
                padding: EdgeInsets.all(0),
                child: Icon(
                  Icons.refresh_outlined,
                  size: 32,
                ),
                onPressed: () {
                  setState(() {
                    _future = getPerformanceSeries();
                  });
                },
              ),
            ],
          );
        },
      ),
    ]);
  }

  Future<List<charts.Series<TickerTotals, String>>> buildInvestmentSeries(
      List<StockMonthlyPerformance> performances) async {
    print("Building series");
    List<TickerTotals> data = performances.map((p) {
      final monthTotal = p.performanceHistory.isNotEmpty
          ? p.performanceHistory.last.monthTotal
          : 0.0;
      return TickerTotals(
          p.ticker, monthTotal, Rgb.random());
    }).toList();
    print("Builded series");
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
