import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/extract/widgets/extract_item_detailed_view.dart';
import 'package:goatfolio/pages/extract/widgets/stock_details.dart';
import 'package:goatfolio/services/investment/model/operation_type.dart';
import 'package:goatfolio/services/investment/model/paginated_extract_result.dart';
import 'package:goatfolio/services/investment/model/stock_investment.dart';
import 'package:goatfolio/utils/extensions.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/utils/modal.dart' as modal;

class ExtractItemView extends StatelessWidget {
  final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
  final ExtractItem item;
  final Function onEdited;
  final Function onDeleted;

  ExtractItemView(
      BuildContext context, this.item, this.onEdited, this.onDeleted,
      {Key? key})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () async {
        await modal.showDraggableModalBottomSheet(
          context,
          ExtractItemDetailedView(item, onEdited, onDeleted),
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
                  child: item.icon.iconWidget,
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
                          item.label,
                          style: textTheme.textStyle.copyWith(fontSize: 12),
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Text(
                          item.key,
                          style: textTheme.textStyle.copyWith(
                              fontSize: 14, fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                    Column(
                      children: <Widget>[
                        Text(
                          formatter.format(item.date).capitalizeWords(),
                          style: textTheme.textStyle.copyWith(fontSize: 12),
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Text(
                          item.value,
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
