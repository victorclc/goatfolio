import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class SummaryPage extends StatelessWidget {
  static const title = 'Resumo';
  static const icon = Icon(CupertinoIcons.chart_bar_square_fill);

  Widget build(BuildContext context) {
    //controller: ScrollController() scroll to the top
    return CustomScrollView(
      slivers: [
        CupertinoSliverNavigationBar(
          largeTitle: Text(title),
          leading: Text("Fevereiro 2020"),
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

              ]),
            ),
          ),
        ),
      ],
    );
  }
}
