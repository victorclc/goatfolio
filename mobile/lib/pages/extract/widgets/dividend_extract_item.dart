import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/investment/model/stock_dividend.dart';
import 'package:goatfolio/utils/extensions.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/utils/modal.dart' as modal;

class DividendExtractItem extends StatelessWidget {
  final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
  final StockDividend dividend;
  final Function onEdited;
  final Function onDeleted;

  DividendExtractItem(
      BuildContext context, this.dividend, this.onEdited, this.onDeleted,
      {Key? key})
      : super(key: key);



  String getValueFromOperation() {
    return "${moneyFormatter.format(dividend.amount)}";
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () async {
        await modal.showDraggableModalBottomSheet(
          context,
          Container(),
          // ExtractDetails(investment, onEdited, onDeleted),
          expandable: false,
          isDismissible: true,
        );
      },
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              Padding(
                padding: EdgeInsets.only(right: 16),
                child: ClipOval(
                  child: Icon(Icons.attach_money, color: Colors.green),
                ),
              ),
              Expanded(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          dividend.label.toLowerCase().capitalizeWords(),
                          style: textTheme.textStyle.copyWith(fontSize: 12),
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Text(
                          dividend.ticker.replaceAll('.SA', ''),
                          style: textTheme.textStyle.copyWith(
                              fontSize: 14, fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                    Column(
                      children: <Widget>[
                        Text(
                          formatter.format(dividend.date).capitalizeWords(),
                          style: textTheme.textStyle.copyWith(fontSize: 12),
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Text(
                          getValueFromOperation(),
                          style: textTheme.textStyle.copyWith(
                              fontWeight: FontWeight.w500, fontSize: 14),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Container(
                  padding: EdgeInsets.only(left: 16),
                  alignment: Alignment.center,
                  child: Icon(
                    Icons.arrow_forward_ios,
                    size: 14,
                    color: Colors.grey,
                  ))
            ],
          ),
          Container(
            padding: EdgeInsets.only(left: 8),
            height: 32,
            child: VerticalDivider(width: 5, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}