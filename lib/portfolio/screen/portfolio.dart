import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/common/widget/expansion_tile_custom.dart';
import 'package:goatfolio/performance/client/performance_client.dart';
import 'package:goatfolio/performance/model/monthly_performance.dart';
import 'package:goatfolio/portfolio/widget/donut_chart.dart';
import 'package:provider/provider.dart';

import 'dart:math' as math;
import 'package:charts_flutter/flutter.dart' as charts;

import 'investment_details.dart';

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
              if (snapshot.hasData) {
                return Column(
                  children: [
                    Container(
                      alignment: Alignment.centerLeft,
                      padding: EdgeInsets.only(left: 16, bottom: 16, top: 8),
                      child: Text(
                        "Alocação",
                        style: Theme.of(context).textTheme.bodyText2.copyWith(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                    ),
                    SizedBox(
                      height: 240,
                      width: double.infinity,
                      child: DonutAutoLabelChart(
                        snapshot.data,
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: ExpansionTileCustom(
                        initiallyExpanded: true,
                        childrenPadding: EdgeInsets.only(left: 8),
                        tilePadding: EdgeInsets.zero,
                        title: Row(
                          children: [
                            Container(
                              width: 4,
                              height: 14,
                              color: Rgb.random().toColor(),
                            ),
                            Text(
                              ' ' + 'Ações',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodyText2
                                  .copyWith(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                            ),
                          ],
                        ),
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: <Widget>[
                              Row(
                                children: <Widget>[
                                  Text(
                                    "Total em carteira",
                                    style:
                                        Theme.of(context).textTheme.bodyText2,
                                  ),
                                ],
                              ),
                              Text(
                                moneyFormatter.format(10.00),
                                style: Theme.of(context).textTheme.bodyText2,
                              ),
                            ],
                          ),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: <Widget>[
                              Row(
                                children: <Widget>[
                                  Text(
                                    "% do portfolio",
                                    style:
                                        Theme.of(context).textTheme.bodyText2,
                                  ),
                                ],
                              ),
                              Text(
                                percentFormatter.format(10.00 / 10.00),
                                style: Theme.of(context).textTheme.bodyText2,
                              ),
                            ],
                          ),
                          SizedBox(
                            height: 24,
                          ),
                          ListView.builder(
                            padding: EdgeInsets.zero,
                            physics: NeverScrollableScrollPhysics(),
                            shrinkWrap: true,
                            itemBuilder: (context, index) {
                              final item = performances[index];
                              final Rgb rgb = colors[item.ticker];
                              var coloredStyle = Theme.of(context)
                                  .textTheme
                                  .bodyText2; //TODO CHANGE COLOR green red
                              var color = rgb.toColor();

                              return StockInvestmentSummaryItem(
                                  performance: item, color: color);
                            },
                            itemCount: performances.length,
                          ),
                        ],
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
      final color = Rgb.random();
      colors[p.ticker] = color;
      if (p.performanceHistory.isEmpty || p.position.currentAmount <= 0) {
        return null;
      }
      return TickerTotals(
          p.ticker, p.performanceHistory.last.monthTotal, color);
    }).toList()
      ..removeWhere((element) => element == null);
    print("Builded series");
    print(data);
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

class StockInvestmentSummaryItem extends StatelessWidget {
  final StockMonthlyPerformance performance;
  final Color color;

  const StockInvestmentSummaryItem(
      {Key key, @required this.performance, @required this.color})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final currentValue = performance.position.currentAmount *
        (performance.currentPrice != null ? performance.currentPrice : 0.0);
    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () {
        navigateToInvestmentDetails(context, performance, color);
      },
      child: Container(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Container(
              padding: EdgeInsets.only(bottom: 8),
              child: Row(
                children: <Widget>[
                  Container(
                    width: 4,
                    height: 14,
                    color: color,
                  ),
                  Text(
                    " ${performance.ticker.replaceAll('.SA', '')}",
                    style: Theme.of(context).textTheme.bodyText2.copyWith(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ],
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "Saldo atual",
                      style: Theme.of(context).textTheme.bodyText2,
                    ),
                  ],
                ),
                Text(
                  moneyFormatter.format(currentValue),
                  style: Theme.of(context).textTheme.bodyText2,
                ),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "Resultado",
                      style: Theme.of(context).textTheme.bodyText2,
                    ),
                  ],
                ),
                Text(
                  moneyFormatter.format(
                      currentValue - performance.position.currentInvested),
                  style: Theme.of(context).textTheme.bodyText2.copyWith(
                      color:
                          currentValue - performance.position.currentInvested <
                                  0
                              ? Colors.red
                              : Colors.green),
                  // style: coloredStyle,
                ),
              ],
            ),
            SizedBox(
              height: 4,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "% do portfolio",
                      style: Theme.of(context).textTheme.bodyText2,
                    ),
                  ],
                ),
                Text(
                  percentFormatter
                      .format(performance.position.currentInvested / 100000),
                  //TODO FIX this
                  style: Theme.of(context).textTheme.bodyText2,
                ),
              ],
            ),
            Divider(
              height: 16,
              color: Colors.grey,
            ),
          ],
        ),
      ),
    );
  }
}
