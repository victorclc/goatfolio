import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/performance/client/performance_client.dart';
import 'package:goatfolio/portfolio/widget/donut_chart.dart';
import 'package:provider/provider.dart';

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
      Container(
        alignment: Alignment.centerLeft,
        padding: EdgeInsets.only(left: 16, bottom: 16, top: 8),
        child: Text(
          "Alocação",
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
      DonutAutoLabelChart([])
    ]);
  }

  List<charts.Series<TickerTotals, String>> _createSubtypeSeries() {
    List<TickerTotals> data = List();
    TickerTotals fixedIncome = TickerTotals(typeDictionary['FIXED_INCOME'], 0);

    consolidated.forEach((subtypeConsolidated) {
      print(typeDictionary[subtypeConsolidated.subtype]);
      if (["CHECKING_ACCOUNT", "POST_FIXED"]
          .contains(subtypeConsolidated.subtype)) {
        fixedIncome.total += subtypeConsolidated.currentPosition;
      } else {
        data.add(new TickerTotals(typeDictionary[subtypeConsolidated.subtype],
            subtypeConsolidated.currentPosition));
      }
      colors[typeDictionary[subtypeConsolidated.subtype]] = createRandomColor();
    });

    if (fixedIncome.total > 0) {
      data.add(fixedIncome);
      colors[typeDictionary['FIXED_INCOME']] = createRandomColor();
    }

    return [
      new charts.Series<TickerTotals, String>(
        id: 'Subtypes',
        domainFn: (TickerTotals totals, _) => totals.ticker,
        measureFn: (TickerTotals totals, _) => totals.total,
        data: data,
        colorFn: (totals, _) => charts.Color(
            r: colors[totals.ticker].r,
            g: colors[totals.ticker].g,
            b: colors[totals.ticker].b),
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

  TickerTotals(this.ticker, this.total);
}

class Rgb {
  final int r;
  final int g;
  final int b;

  Rgb(this.r, this.g, this.b);

  Color toColor() {
    return Color.fromARGB(0xFF, this.r, this.g, this.b);
  }
}
