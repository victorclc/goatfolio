import 'package:flutter/cupertino.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/linear_chart.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/common/extension/string.dart';

import 'money_date_series.dart';

class RentabilityChart extends StatefulWidget {
  final List<charts.Series> rentabilitySeries;

  const RentabilityChart({Key key, this.rentabilitySeries}) : super(key: key);

  @override
  _RentabilityChartState createState() => _RentabilityChartState();
}

class _RentabilityChartState extends State<RentabilityChart> {
  MoneyDateSeries selectedGrossSeries;
  MoneyDateSeries selectedIbovSeries;
  final dateFormat = DateFormat('MMMM', 'pt_BR');

  @override
  void initState() {
    super.initState();
    selectedGrossSeries = widget.rentabilitySeries.first.data.last;
    selectedIbovSeries = widget.rentabilitySeries.last.data.last;
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    setState(() {
      selectedGrossSeries = series['Rentabilidade'];
      selectedIbovSeries = series['IBOV'];
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
                'Rentabilidade',
                style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
              ),
              Text(
                percentFormatter.format(selectedGrossSeries.money / 100),
                style: textTheme.textStyle
                    .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
              ),
              Text(
                'Ibovespa',
                style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
              ),
              Text(
                percentFormatter.format(selectedIbovSeries.money / 100),
                style: textTheme.textStyle
                    .copyWith(fontSize: 20, fontWeight: FontWeight.w500),
              ),
              Text(
                '${dateFormat.format(selectedGrossSeries.date).capitalize()} de ${selectedGrossSeries.date.year}',
                style: textTheme.tabLabelTextStyle
                    .copyWith(fontSize: 16, fontWeight: FontWeight.w400),
              ),
            ],
          ),
        ),
        SizedBox(
          height: 240,
          child: LinearChart(
            widget.rentabilitySeries,
            onSelectionChanged: onSelectionChanged,
          ),
        ),
      ],
    );
  }
}
