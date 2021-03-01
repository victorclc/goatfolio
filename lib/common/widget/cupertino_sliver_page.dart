import 'package:flutter/cupertino.dart';

class CupertinoSliverPage extends StatelessWidget {
  final ScrollController controller;
  final String largeTitle;
  final Function onRefresh;
  final List<Widget> children;

  const CupertinoSliverPage({
    Key key,
    @required this.largeTitle,
    @required this.children,
    this.onRefresh,
    this.controller,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      controller: controller,
      slivers: [
        CupertinoSliverNavigationBar(
          largeTitle: Text(largeTitle),
        ),
        CupertinoSliverRefreshControl(
          onRefresh: () => Future.delayed(Duration(seconds: 5)),
        ),
        SliverSafeArea(
          top: false,
          sliver: SliverPadding(
            padding: EdgeInsets.symmetric(vertical: 12),
            sliver: SliverList(
              delegate: SliverChildListDelegate.fixed(children),
            ),
          ),
        ),
      ],
    );
  }
}