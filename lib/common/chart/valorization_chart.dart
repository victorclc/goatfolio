import 'package:flutter/cupertino.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/linear_chart.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/common/extension/string.dart';

import 'money_date_series.dart';

class ValorizationChart extends StatefulWidget {
  final Future<List<charts.Series>> totalAmountSeries;

  const ValorizationChart({Key key, this.totalAmountSeries}) : super(key: key);

  @override
  _ValorizationChartState createState() => _ValorizationChartState();
}

class _ValorizationChartState extends State<ValorizationChart> {
  MoneyDateSeries selectedGrossSeries;
  MoneyDateSeries selectedInvestedSeries;
  final dateFormat = DateFormat('MMMM', 'pt_BR');

  @override
  void initState() {
    super.initState();
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    setState(() {
      selectedGrossSeries = series['Saldo bruto'];
      selectedInvestedSeries = series['Valor investido'];
    });
  }

  Widget buildHeader() {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Container(
      padding: EdgeInsets.only(top: 4),
      alignment: Alignment.centerLeft,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Saldo bruto',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          Text(
            selectedGrossSeries != null
                ? moneyFormatter.format(selectedGrossSeries.money)
                : moneyFormatter.format(0),
            style: textTheme.textStyle
                .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
          ),
          Text(
            'Valor investido',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          Text(
            selectedInvestedSeries != null
                ? moneyFormatter.format(selectedInvestedSeries.money)
                : moneyFormatter.format(0),
            style: textTheme.textStyle
                .copyWith(fontSize: 20, fontWeight: FontWeight.w500),
          ),
          Text(
            selectedGrossSeries != null
                ? '${dateFormat.format(selectedGrossSeries.date).capitalize()} de ${selectedGrossSeries.date.year}'
                : '${dateFormat.format(DateTime.now()).capitalize()} de ${DateTime.now().year}',
            style: textTheme.tabLabelTextStyle
                .copyWith(fontSize: 16, fontWeight: FontWeight.w400),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return FutureBuilder(
      future: widget.totalAmountSeries,
      builder: (context, snapshot) {
        switch (snapshot.connectionState) {
          case ConnectionState.none:
          case ConnectionState.active:
            break;
          case ConnectionState.waiting:
            return Column(
              children: [
                buildHeader(),
                SizedBox(height: 240, child: CupertinoActivityIndicator()),
              ],
            );
          case ConnectionState.done:
            if (snapshot.hasData) {
              if (selectedGrossSeries == null) {
                selectedGrossSeries = snapshot.data.first.data.last;
              }
              if (selectedInvestedSeries == null) {
                selectedInvestedSeries = snapshot.data.last.data.last;
              }
              return Column(
                children: [
                  buildHeader(),
                  SizedBox(
                    height: 240,
                    child: LinearChart(
                      snapshot.data,
                      onSelectionChanged: onSelectionChanged,
                    ),
                  ),
                ],
              );
            } else {
              return Column(
                children: [
                  buildHeader(),
                  SizedBox(
                    height: 240,
                    child: Center(
                      child: Text(
                        "Nenhum dado ainda.",
                        style: textTheme.textStyle,
                      ),
                    ),
                  ),
                ],
              );
            }
        }
        return Text("deu algum erro");
      },
    );
  }
}
