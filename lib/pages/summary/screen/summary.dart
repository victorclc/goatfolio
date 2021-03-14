import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/summary/widget/month_summary_card.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/common/extension/string.dart';

class SummaryPage extends StatefulWidget {
  static const title = 'Resumo';
  static const icon = Icon(CupertinoIcons.chart_bar_square_fill);

  @override
  _SummaryPageState createState() => _SummaryPageState();
}

class _SummaryPageState extends State<SummaryPage> {
  @override
  void initState() {
    super.initState();
  }

  Widget build(BuildContext context) {
    //controller: ScrollController() scroll to the top
    return CustomScrollView(
      slivers: [
        CupertinoSliverNavigationBar(
          largeTitle: Text(SummaryPage.title),
          leading: Text(
            DateFormat("MMMM yyyy", 'pt_BR')
                .format(DateTime.now())
                .capitalize(),
            style: Theme.of(context)
                .textTheme
                .subtitle2
                .copyWith(fontWeight: FontWeight.w400),
          ),
          trailing: CupertinoButton(
            padding: EdgeInsets.zero,
            child: Icon(
              CupertinoIcons.bell,
              color: Colors.black,
            ),
            onPressed: () => print("BELL"),
          ),
        ),
        CupertinoSliverRefreshControl(
          onRefresh: () => Future.delayed(Duration(seconds: 5)),
        ),
        SliverSafeArea(
          top: false,
          sliver: SliverPadding(
            padding: EdgeInsets.symmetric(vertical: 12),
            sliver: SliverList(
              delegate: SliverChildListDelegate.fixed([
                MonthSummaryCard(),
              ]),
            ),
          ),
        ),
      ],
    );
  }
}
