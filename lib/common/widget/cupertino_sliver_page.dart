import 'package:flutter/cupertino.dart';

class CupertinoSliverPage extends StatelessWidget {
  final String largeTitle;
  final Function onRefresh;
  final List<Widget> children;
  final Function onScrollNotification;

  const CupertinoSliverPage({
    Key key,
    @required this.largeTitle,
    @required this.children,
    this.onRefresh,
    this.onScrollNotification,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: onScrollNotification,
      child: CustomScrollView(
        slivers: [
          CupertinoSliverNavigationBar(
            leading: Container(),
            heroTag: 'portfolioNavBar',
            largeTitle: Text(largeTitle),
            backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          ),
          onRefresh != null
              ? CupertinoSliverRefreshControl(
                  onRefresh: onRefresh,
                )
              : SliverList(
                  delegate: SliverChildListDelegate.fixed([Container()])),
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
      ),
    );
  }
}
