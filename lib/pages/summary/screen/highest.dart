import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';

void goToHighestPage(
    BuildContext context, PortfolioPerformance performance, {bool sortAscending = false}) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => HighestPage(performance: performance, startAscending: sortAscending),
    ),
  );
}

class HighestPage extends StatefulWidget {
  final PortfolioPerformance performance;
  final bool startAscending;

  const HighestPage({Key key, this.performance, this.startAscending}) : super(key: key);

  @override
  _HighestPageState createState() => _HighestPageState();
}

class _HighestPageState extends State<HighestPage> {
  int sortColumnIndex;
  bool sortAscending;
  List<StockPerformance> allStocks;

  @override
  void initState() {
    super.initState();
    sortColumnIndex = 2;
    sortAscending = widget.startAscending;
    allStocks = sortByVariation(widget.startAscending);
  }

  List<StockPerformance> sortByTicker(bool ascending) {
    return (widget.performance.stocks + widget.performance.reits)
      ..sort((b, a) {
        if (ascending)
          return b.ticker.compareTo(a.ticker);
        else
          return a.ticker.compareTo(b.ticker);
      });
  }

  List<StockPerformance> sortByPrice(bool ascending) {
    return (widget.performance.stocks + widget.performance.reits)
      ..sort((b, a) {
        if (ascending)
          return b.currentStockPrice.compareTo(a.currentStockPrice);
        else
          return a.currentStockPrice.compareTo(b.currentStockPrice);
      });
  }

  List<StockPerformance> sortByVariation(bool ascending) {
    return (widget.performance.stocks + widget.performance.reits)
      ..sort((b, a) {
        if (ascending)
          return b.currentDayChangePercent.compareTo(a.currentDayChangePercent);
        else
          return a.currentDayChangePercent.compareTo(b.currentDayChangePercent);
      });
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          previousPageTitle: "",
          middle: Text("Altas e Baixas"),
        ),
        child: SingleChildScrollView(
            child: SafeArea(
          child: Container(
              padding: EdgeInsets.only(bottom: 16),
              child: DataTable(
                dividerThickness: 0.00001,
                dataRowHeight: 48,
                sortColumnIndex: sortColumnIndex,
                sortAscending: sortAscending,
                columns: [
                  DataColumn(
                      label: Text('Ativo',
                          style: textTheme.textStyle.copyWith(fontSize: 16)),
                      onSort: (index, ascending) {
                        setState(() {
                          allStocks = sortByTicker(ascending);
                          sortAscending = ascending;
                          sortColumnIndex = index;
                        });
                      }),
                  DataColumn(
                      label: Text('Preço',
                          style: textTheme.textStyle.copyWith(fontSize: 16)),
                      numeric: true,
                      onSort: (index, ascending) {
                        setState(() {
                          allStocks = sortByPrice(ascending);
                          sortAscending = ascending;
                          sortColumnIndex = index;
                        });
                      }),
                  DataColumn(
                      label: Text('Variação',
                          style: textTheme.textStyle.copyWith(fontSize: 16)),
                      numeric: true,
                      onSort: (index, ascending) {
                        setState(() {
                          allStocks = sortByVariation(ascending);
                          sortAscending = ascending;
                          sortColumnIndex = index;
                        });
                      }),
                ],
                rows: allStocks
                    .map((e) => DataRow(cells: [
                          DataCell(
                              Text(
                                e.ticker,
                                style:
                                    textTheme.textStyle.copyWith(fontSize: 16),
                              ),
                              placeholder: true),
                          DataCell(
                            Text(
                              moneyFormatter.format(e.currentStockPrice),
                              style: textTheme.textStyle.copyWith(fontSize: 16),
                            ),
                          ),
                          DataCell(
                            Text(
                              percentFormatter
                                  .format(e.currentDayChangePercent / 100),
                              style: textTheme.textStyle.copyWith(
                                  fontSize: 16,
                                  color: e.currentDayChangePercent >= 0
                                      ? Colors.green
                                      : Colors.red),
                            ),
                          ),
                        ]))
                    .toList(),
              )),
        )));
  }

  Widget buildList(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    List<Widget> children = [];
    final stocks = widget.performance.stocks
      ..sort((b, a) =>
          a.currentDayChangePercent.compareTo(b.currentDayChangePercent));

    stocks.forEach(
      (s) {
        children.add(Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(s.ticker, style: textTheme.textStyle.copyWith(fontSize: 14)),
            Text(moneyFormatter.format(s.currentStockPrice)),
            Text(
              percentFormatter.format(s.currentDayChangePercent / 100),
              style: textTheme.textStyle
                  .copyWith(fontSize: 14, color: Colors.green),
            ),
          ],
        ));
        children.add(SizedBox(
          height: 32,
        ));
      },
    );

    return Column(
      children: children,
    );
  }
}
