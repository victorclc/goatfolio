import 'package:flutter/cupertino.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/linear_chart.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/common/extension/string.dart';

import 'money_date_series.dart';

class ValorizationChart extends StatefulWidget {
  final List<charts.Series> totalAmountSeries;

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
    // selectedGrossSeries = widget.totalAmountSeries.first.data.last;
    // selectedInvestedSeries = widget.totalAmountSeries.last.data.last;
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    setState(() {
      selectedGrossSeries = series['Saldo bruto'];
      selectedInvestedSeries = series['Valor investido'];
    });
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Column(
      children: [
        Container(
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
        ),
        SizedBox(
          height: 240,
          child: widget.totalAmountSeries != null
              ? LinearChart(
                  widget.totalAmountSeries,
                  onSelectionChanged: onSelectionChanged,
                )
              : Center(
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
