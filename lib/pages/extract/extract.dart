import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/util/focus.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/pages/add/screen/stock_add.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';

import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:goatfolio/common/extension/string.dart';
import 'dart:math' as math;
import 'details.dart';

class ExtractPage extends StatefulWidget {
  static const title = 'Extrato';
  static const icon = Icon(Icons.view_list);

  @override
  _ExtractPageState createState() => _ExtractPageState();
}

class _ExtractPageState extends State<ExtractPage> {
  static const int limit = 20;
  final DateFormat monthFormatter = DateFormat('MMMM', 'pt_BR');
  TextEditingController searchController = TextEditingController();
  StockInvestmentService stockService;
  List<StockInvestment> investments;
  Future<List<StockInvestment>> _future;
  int offset = 0;
  bool scrollLoading = false;
  bool searching = false;

  ScrollController controller;

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    stockService = StockInvestmentService(userService);
    _future = getInvestments();
  }

  bool scrollListener(ScrollNotification notification) {
    // print(notification);
    FocusUtils.unfocus(context);
    if (!searching &&
        notification is ScrollEndNotification &&
        notification.metrics.extentAfter <= 100) {
      loadMoreInvestments();
    }
    return false;
  }

  Future<List<StockInvestment>> getInvestments() async {
    final data =
        await stockService.getInvestments(limit: limit, offset: offset);
    if (data != null && data.isNotEmpty) {
      offset += data.length;
    }
    return data;
  }

  Future<List<StockInvestment>> getInvestmentsTicker(String ticker) async {
    return await stockService.getByTicker(ticker);
  }

  void loadMoreInvestments() async {
    print("loading more investments");
    setState(() {
      scrollLoading = true;
    });
    final data = await getInvestments();

    setState(() {
      investments.addAll(data);
      scrollLoading = false;
    });
  }

  Future<void> onRefresh() async {
    await stockService.refreshInvestments();
    offset = 0;
    _future = getInvestments();
    await _future;
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    DateTime prevDateTime;
    return NotificationListener<ScrollNotification>(
      onNotification: scrollListener,
      child: GestureDetector(
        onTap: () => FocusUtils.unfocus(context),
        onVerticalDragStart: (_) => FocusUtils.unfocus(context),
        onPanStart: (_) => FocusUtils.unfocus(context),
        child: CustomScrollView(
          controller: controller,
          slivers: [
            CupertinoSliverNavigationBar(
              largeTitle: Text(ExtractPage.title),
              backgroundColor:
                  CupertinoTheme.of(context).scaffoldBackgroundColor,
              border: Border(),
            ),
            buildSliverTextSearchField(),
            !searching
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
                  delegate: SliverChildListDelegate.fixed(
                    [
                      FutureBuilder(
                        future: _future,
                        builder: (context, snapshot) {
                          switch (snapshot.connectionState) {
                            case ConnectionState.none:
                            case ConnectionState.active:
                              break;
                            case ConnectionState.waiting:
                              return CupertinoActivityIndicator();
                            case ConnectionState.done:
                              if (snapshot.hasData) {
                                investments = snapshot.data;
                                if (investments.isEmpty) {
                                  return Center(
                                    child: Text(
                                      "Nenhuma movimentação cadastrada",
                                      style: CupertinoTheme.of(context)
                                          .textTheme
                                          .textStyle,
                                    ),
                                  );
                                }
                                return Column(
                                  children: [
                                    Container(
                                      padding:
                                          EdgeInsets.only(left: 16, right: 16),
                                      child: ListView.builder(
                                        padding: EdgeInsets.zero,
                                        physics: NeverScrollableScrollPhysics(),
                                        shrinkWrap: true,
                                        itemCount: investments.length,
                                        itemBuilder: (context, index) {
                                          final investment = investments[index];
                                          if (prevDateTime == null ||
                                              investment.date.month !=
                                                  prevDateTime.month) {
                                            prevDateTime = investment.date;
                                            return Column(
                                              children: [
                                                Container(
                                                  width: double.infinity,
                                                  padding: EdgeInsets.only(
                                                      bottom: 16),
                                                  alignment:
                                                      Alignment.centerLeft,
                                                  child: Text(
                                                    '${monthFormatter.format(investment.date).capitalize()} de ${investment.date.year}',
                                                    style: CupertinoTheme.of(
                                                            context)
                                                        .textTheme
                                                        .navTitleTextStyle,
                                                  ),
                                                ),
                                                _StockExtractItem(
                                                    context,
                                                    investments[index],
                                                    onEditCb,
                                                    onDeleteCb)
                                              ],
                                            );
                                          }
                                          prevDateTime = investment.date;
                                          return _StockExtractItem(
                                              context,
                                              investments[index],
                                              onEditCb,
                                              onDeleteCb);
                                        },
                                      ),
                                    ),
                                    scrollLoading
                                        ? CupertinoActivityIndicator()
                                        : Container(),
                                  ],
                                );
                              }
                          }
                          return _LoadingError(
                            onPressed: () {
                              setState(() {
                                _future = getInvestments();
                              });
                            },
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void onEditCb(StockInvestment investment) async {
    await ModalUtils.showDragableModalBottomSheet(
      context,
      StockAdd.fromStockInvestment(
        investment,
        userService: Provider.of<UserService>(context, listen: false),
      ),
    );
    setState(() {});
  }

  void onDeleteCb(StockInvestment investment) async {
    final deleteFuture = stockService.deleteInvestment(investment);
    setState(() {
      investments.remove(investment);
      offset--;
    });
    final data = await getInvestments();
    if (data != null && data.isNotEmpty) {
      setState(() {
        investments.addAll(data);
      });
    }
  }

  SliverPersistentHeader buildSliverTextSearchField() {
    return SliverPersistentHeader(
      pinned: true,
      delegate: _SliverAppBarDelegate(
        minHeight: 76,
        maxHeight: 76,
        child: Column(
          children: [
            Container(
              decoration: BoxDecoration(
                color:CupertinoTheme.of(context).scaffoldBackgroundColor ,
                border: Border(
                  bottom: BorderSide(
                    color: Color(0x4D000000),
                    width: 0.0, // One physical pixel.
                    style: BorderStyle.solid,
                  ),
                ),
              ),
              padding: EdgeInsets.all(16),
              child: CupertinoSearchTextField(
                controller: searchController,
                onChanged: (value) {
                  setState(() {
                    if (value.isNotEmpty) {
                      searching = true;
                      _future = getInvestmentsTicker(value);
                    } else {
                      offset = 0;
                      searching = false;
                      _future = getInvestments();
                    }
                  });
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LoadingError extends StatelessWidget {
  final Function onPressed;

  const _LoadingError({Key key, @required this.onPressed}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        SizedBox(
          height: 32,
        ),
        Text("Tivemos um problema ao carregar", style: textTheme.textStyle),
        Text(" as transações.", style: textTheme.textStyle),
        SizedBox(
          height: 8,
        ),
        Text("Toque para tentar novamente.", style: textTheme.textStyle),
        CupertinoButton(
          padding: EdgeInsets.all(0),
          child: Icon(
            Icons.refresh_outlined,
            size: 32,
          ),
          onPressed: onPressed,
        ),
      ],
    );
  }
}

class _StockExtractItem extends StatelessWidget {
  final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
  final StockInvestment investment;
  final Function onEdited;
  final Function onDeleted;

  _StockExtractItem(
      BuildContext context, this.investment, this.onEdited, this.onDeleted,
      {Key key})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () async {
        await ModalUtils.showDragableModalBottomSheet(
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
                  child: Icon(
                    investment.operation == "BUY"
                        ? Icons.trending_up
                        : Icons.trending_down,
                    color: investment.operation == "BUY"
                        ? Colors.green
                        : Colors.red,
                  ),
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
                          investment.operation == "BUY" ? "Compra" : "Venda",
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
                          "${moneyFormatter.format(investment.price * investment.amount)}",
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

class _SliverAppBarDelegate extends SliverPersistentHeaderDelegate {
  _SliverAppBarDelegate({
    @required this.minHeight,
    @required this.maxHeight,
    @required this.child,
  });

  final double minHeight;
  final double maxHeight;
  final Widget child;

  @override
  double get minExtent => minHeight;

  @override
  double get maxExtent => math.max(maxHeight, minHeight);

  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    return new SizedBox.expand(child: child);
  }

  @override
  bool shouldRebuild(_SliverAppBarDelegate oldDelegate) {
    return maxHeight != oldDelegate.maxHeight ||
        minHeight != oldDelegate.minHeight ||
        child != oldDelegate.child;
  }
}
