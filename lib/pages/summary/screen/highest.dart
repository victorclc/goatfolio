import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/services/performance/model/stock_variation.dart';

void goToHighestPage(BuildContext context, List<StockVariation> stocksVariation,
    {bool sortAscending = false}) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => HighestPage(
          stocksVariation: stocksVariation, startAscending: sortAscending),
    ),
  );
}

class HighestPage extends StatefulWidget {
  final List<StockVariation> stocksVariation;
  final bool startAscending;

  const HighestPage({Key key, this.stocksVariation, this.startAscending})
      : super(key: key);

  @override
  _HighestPageState createState() => _HighestPageState();
}

class _HighestPageState extends State<HighestPage> {
  int sortColumnIndex;
  bool sortAscending;
  List<StockVariation> allStocks;

  @override
  void initState() {
    super.initState();
    sortColumnIndex = 2;
    sortAscending = widget.startAscending;
    allStocks = sortByVariation(widget.startAscending);
  }

  List<StockVariation> sortByTicker(bool ascending) {
    return widget.stocksVariation
      ..sort((b, a) {
        if (ascending)
          return b.ticker.compareTo(a.ticker);
        else
          return a.ticker.compareTo(b.ticker);
      });
  }

  List<StockVariation> sortByPrice(bool ascending) {
    return widget.stocksVariation
      ..sort((b, a) {
        if (ascending)
          return b.lastPrice.compareTo(a.lastPrice);
        else
          return a.lastPrice.compareTo(b.lastPrice);
      });
  }

  List<StockVariation> sortByVariation(bool ascending) {
    return widget.stocksVariation
      ..sort((b, a) {
        if (ascending)
          return b.variation.compareTo(a.variation);
        else
          return a.variation.compareTo(b.variation);
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
                            Container(
                              width: 68,
                              alignment: Alignment.centerRight,
                              child: Text(
                                moneyFormatter.format(e.lastPrice),
                                style:
                                    textTheme.textStyle.copyWith(fontSize: 16),
                              ),
                            ),
                          ),
                          DataCell(
                            Text(
                              percentFormatter.format(e.variation / 100),
                              style: textTheme.textStyle.copyWith(
                                  fontSize: 16,
                                  color: e.variation >= 0
                                      ? Colors.green
                                      : Colors.red),
                            ),
                          ),
                        ]))
                    .toList(),
              )),
        )));
  }
}
