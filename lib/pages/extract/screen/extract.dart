import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/search/cupertino_search_delegate.dart';
import 'package:goatfolio/common/util/focus.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/pages/add/screen/stock_add.dart';
import 'package:goatfolio/pages/extract/search/delegate.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/model/operation_type.dart';

import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:goatfolio/common/extension/string.dart';
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
  bool fetchingContent;

  ScrollController controller;

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    stockService = StockInvestmentService(userService);
    fetchingContent = true;
    _future = getInvestments();
  }

  bool scrollListener(ScrollNotification notification) {
    FocusUtils.unfocus(context);
    if (notification is ScrollEndNotification &&
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
      scrollLoading = false;
      if (data != null) {
        investments.addAll(data);
      }
    });
  }

  Future<void> onRefresh() async {
    if (!fetchingContent) {
      await stockService.refreshInvestments();
      offset = 0;
      _future = getInvestments();
      await _future;
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
  }

  Widget buildIos(BuildContext context) {
    return buildContent(context);
  }

  Widget buildAndroid(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefresh,
      child: buildContent(context),
    );
  }

  void _showSearch() {
    showCupertinoSearch(
        context: context,
        delegate: ExtractSearchDelegate(
          getInvestmentsTicker,
          buildExtractList,
        ),
        placeHolderText: "Buscar ativo");
  }

  Widget buildContent(BuildContext context) {
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
              heroTag: 'extractNavBar',
              largeTitle: Text(ExtractPage.title),
              backgroundColor:
                  CupertinoTheme.of(context).scaffoldBackgroundColor,
              trailing: IconButton(
                icon: Icon(CupertinoIcons.search),
                onPressed: _showSearch,
                padding: EdgeInsets.zero,
                alignment: Alignment.centerRight,
              ),
            ),
            if (Platform.isIOS)
              CupertinoSliverRefreshControl(
                onRefresh: onRefresh,
              ),
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
                              return Platform.isIOS
                                  ? CupertinoActivityIndicator()
                                  : Center(child: CircularProgressIndicator());
                            case ConnectionState.done:
                              if (snapshot.hasData) {
                                fetchingContent = false;
                                investments = snapshot.data;
                                return buildExtractList(context, snapshot.data);
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

  Widget buildExtractList(
      BuildContext context, List<StockInvestment> investments) {
    DateTime prevDateTime;
    if (investments.isEmpty) {
      return Center(
        child: Text(
          "Nenhuma movimentação cadastrada",
          style: CupertinoTheme.of(context).textTheme.textStyle,
        ),
      );
    }
    return Column(
      children: [
        Container(
          padding: EdgeInsets.only(left: 16, right: 16),
          child: ListView.builder(
            padding: EdgeInsets.zero,
            physics: NeverScrollableScrollPhysics(),
            shrinkWrap: true,
            itemCount: investments.length,
            itemBuilder: (context, index) {
              final investment = investments[index];
              if (prevDateTime == null ||
                  investment.date.month != prevDateTime.month) {
                prevDateTime = investment.date;
                return Column(
                  children: [
                    Container(
                      width: double.infinity,
                      padding: EdgeInsets.only(bottom: 16),
                      alignment: Alignment.centerLeft,
                      child: Text(
                        '${monthFormatter.format(investment.date).capitalize()} de ${investment.date.year}',
                        style: CupertinoTheme.of(context)
                            .textTheme
                            .navTitleTextStyle,
                      ),
                    ),
                    _StockExtractItem(
                        context, investments[index], onEditCb, onDeleteCb)
                  ],
                );
              }
              prevDateTime = investment.date;
              return _StockExtractItem(
                  context, investments[index], onEditCb, onDeleteCb);
            },
          ),
        ),
        scrollLoading ? Platform.isIOS
            ? CupertinoActivityIndicator()
            : Center(child: CircularProgressIndicator()) : Container(),
      ],
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
    stockService.deleteInvestment(investment);
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
