import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/extract/widgets/stock_details.dart';
import 'package:goatfolio/services/investment/model/operation_type.dart';
import 'package:goatfolio/services/investment/model/stock_investment.dart';
import 'package:goatfolio/utils/extensions.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/utils/modal.dart' as modal;

class StockExtractItem extends StatelessWidget {
  final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
  final StockInvestment investment;
  final Function onEdited;
  final Function onDeleted;

  StockExtractItem(
      BuildContext context, this.investment, this.onEdited, this.onDeleted,
      {Key? key})
      : super(key: key);

  Icon getIconFromOperation(String operation) {
    switch (operation) {
      case OperationType.BUY:
        return Icon(Icons.trending_up, color: Colors.green);
      case OperationType.SELL:
        return Icon(Icons.trending_down, color: Colors.red);
      case OperationType.SPLIT:
      case OperationType.INCORP_ADD:
        return Icon(Icons.call_split, color: Colors.brown);
      case OperationType.GROUP:
      case OperationType.INCORP_SUB:
        return Icon(Icons.group_work_outlined, color: Colors.brown);
      default:
        return Icon(Icons.clear);
    }
  }

  String getLabelFromOperation(String operation) {
    switch (operation) {
      case OperationType.BUY:
        return "Compra";
      case OperationType.SELL:
        return "Venda";
      case OperationType.SPLIT:
        return "Desdobramento";
      case OperationType.INCORP_SUB:
      case OperationType.INCORP_ADD:
        return "Incorporação";
      case OperationType.GROUP:
        return "Grupamento";
      default:
        return "";
    }
  }

  String getValueFromOperation(String operation) {
    switch (operation) {
      case OperationType.BUY:
        return "${moneyFormatter.format(investment.price * investment.amount)}";
      case OperationType.SELL:
        return "${moneyFormatter.format(investment.price * investment.amount)}";
      case OperationType.SPLIT:
      case OperationType.INCORP_ADD:
        return "+${investment.amount} unid.";
      case OperationType.INCORP_SUB:
      case OperationType.GROUP:
        return "-${investment.amount} unid.";
      default:
        return "";
    }
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () async {
        await modal.showDraggableModalBottomSheet(
          context,
          ExtractDetails(investment, onEdited, onDeleted),
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
                  child: getIconFromOperation(investment.operation),
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
                          getLabelFromOperation(investment.operation),
                          style: textTheme.textStyle.copyWith(fontSize: 12),
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Text(
                          investment.ticker.replaceAll('.SA', ''),
                          style: textTheme.textStyle.copyWith(
                              fontSize: 14, fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                    Column(
                      children: <Widget>[
                        Text(
                          formatter.format(investment.date).capitalizeWords(),
                          style: textTheme.textStyle.copyWith(fontSize: 12),
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Text(
                          getValueFromOperation(investment.operation),
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
