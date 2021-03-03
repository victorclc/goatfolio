import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/bottom_sheet_page.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/extract/screen/details.dart';
import 'package:goatfolio/investment/client/portfolio.dart';
import 'package:goatfolio/investment/model/stock.dart';
import 'package:goatfolio/investment/service/stock_investment_service.dart';
import 'package:goatfolio/investment/storage/stock_investment.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:goatfolio/common/extension/string.dart';

class ExtractPage extends StatefulWidget {
  static const title = 'Extrato';
  static const icon = Icon(Icons.view_list);

  @override
  _ExtractPageState createState() => _ExtractPageState();
}

class _ExtractPageState extends State<ExtractPage> {
  ScrollController controller;
  PortfolioClient client;
  StockInvestmentStorage storage;
  StockInvestmentService stockService;
  List<StockInvestment> investments;
  Future<List<StockInvestment>> _future;
  static const int limit = 20;
  int offset = 0;
  bool scrollLoading = false;

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    client = PortfolioClient(userService);
    stockService = StockInvestmentService(userService);
    storage = StockInvestmentStorage();
    _future = getInvestments();
  }

  @override
  void dispose() {
    super.dispose();
  }

  bool _scrollListener(ScrollNotification notification) {
    // print(notification);
    if (notification is ScrollEndNotification &&
        notification.metrics.extentAfter <= 100) {
      loadMoreInvestments();
    }
    return false;
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
    print("BUSCANDO");
    final int timestamp = investments[0].date.millisecondsSinceEpoch ~/ 1000;
    List<StockInvestment> data = await client.getInvestments(timestamp, 'ge');
    print(data);
    data.forEach((i) async => await storage.insert(i));
    setState(() {
      investments = null;
      resetState();
    });
  }

  void resetState() {
    offset = 0;
    investments = null;
    _future = getInvestments();
  }

  void onEditCb() {
    setState(() {});
  }

  void onDeleteCb(StockInvestment investment) async {
    await stockService.deleteInvestment(investment);

    setState(() {
      investments.remove(investment);
      offset--;
    });
    final data = await getStorageInvestments(limit: 1);
    if (data != null && data.isNotEmpty) {
      setState(() {
        investments.addAll(data);
      });
    }
  }

  Future<List<StockInvestment>> getInvestments() async {
    // await deleteInvestmentsDatabase();
    final data = await getStorageInvestments();
    if ((data == null || data.isEmpty) &&
        (investments == null || investments.isEmpty)) {
      debugPrint("Buscando na API");
      List<StockInvestment> investments = await client.getInvestments();
      investments.forEach((i) async => await storage.insert(i));
      return getStorageInvestments();
    }
    return data;
  }

  Future<List<StockInvestment>> getStorageInvestments({limit = limit}) async {
    debugPrint("getInvestmentsPaginated(offset: $offset, limit: $limit");
    final data = await storage.getPaginated(offset, limit);
    if (data != null && data.isNotEmpty) {
      this.offset += limit;
    }
    return data;
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoSliverPage(
      largeTitle: ExtractPage.title,
      onScrollNotification: _scrollListener,
      onRefresh: onRefresh,
      children: [
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
                            return StockExtractItem(context, investments[index],
                                onEditCb, onDeleteCb);
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
            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(
                  height: 32,
                ),
                Text("Tivemos um problema ao carregar",
                    style: Theme.of(context).textTheme.subtitle1),
                Text(" as transações.",
                    style: Theme.of(context).textTheme.subtitle1),
                SizedBox(
                  height: 8,
                ),
                Text("Toque para tentar novamente.",
                    style: Theme.of(context).textTheme.subtitle1),
                CupertinoButton(
                  padding: EdgeInsets.all(0),
                  child: Icon(
                    Icons.refresh_outlined,
                    size: 32,
                  ),
                  onPressed: () {
                    setState(() {
                      _future = getInvestments();
                    });
                  },
                ),
              ],
            );
          },
        ),
      ],
    );
  }
}

class StockExtractItem extends StatelessWidget {
  final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
  final StockInvestment investment;
  final Function onEdited;
  final Function onDeleted;

  StockExtractItem(
      BuildContext context, this.investment, this.onEdited, this.onDeleted,
      {Key key})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () async {
        await ModalUtils.showDragableModalBottomSheet(
          context,
          BottomSheetPage(
            child: ExtractDetails(investment, onEdited, onDeleted),
          ),
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
                          style: Theme.of(context)
                              .textTheme
                              .bodyText2
                              .copyWith(fontSize: 12),
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Text(
                          investment.ticker.replaceAll('.SA', ''),
                          style: Theme.of(context)
                              .textTheme
                              .bodyText2
                              .copyWith(fontWeight: FontWeight.w600),
                        ),
                      ],
                    ),
                    Column(
                      children: <Widget>[
                        Text(
                          formatter.format(investment.date).capitalizeWords(),
                          style: Theme.of(context)
                              .textTheme
                              .bodyText2
                              .copyWith(fontSize: 12),
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Text(
                          "${moneyFormatter.format(investment.price * investment.amount)}",
                          style: Theme.of(context)
                              .textTheme
                              .bodyText2
                              .copyWith(fontWeight: FontWeight.w600),
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
