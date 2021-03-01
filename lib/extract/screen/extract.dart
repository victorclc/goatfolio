import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/investment/client/portfolio.dart';
import 'package:goatfolio/investment/model/stock.dart';
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
  List<StockInvestment> investments;
  Future<List<StockInvestment>> _future;
  final int limit = 10;
  int offset;
  bool scrollLoading = false;

  @override
  void initState() {
    super.initState();
    client = PortfolioClient(Provider.of<UserService>(context, listen: false));
    storage = StockInvestmentStorage();
    controller = new ScrollController()..addListener(_scrollListener);
    _future = getInvestments();
    offset = 0;
  }

  @override
  void dispose() {
    controller.removeListener(_scrollListener);
    super.dispose();
  }

  void _scrollListener() async {
    if (controller.position.extentAfter == 0 && !scrollLoading) {
      scrollLoading = true;
      print(controller.position.extentAfter);
      final data = await getInvestments();
      await Future.delayed(Duration(seconds: 5));
      setState(() {
        investments.addAll(data);
      });
      scrollLoading = false;
    }
  }

  Future<List<StockInvestment>> getInvestments() async {
    final data = await storage.getPaginated(offset, limit);
    if (data != null && data.isNotEmpty) {
      offset++;
    }
    return data;
  }

  // void testing() async {
  //   var storage = StockInvestmentStorage();
  //   // List<StockInvestment> investments = await client.getInvestments();
  //   // await investments.forEach((i) async => await storage.insert(i));
  //   debugPrint("SQLITE INVESTMENTS");
  //   print(await storage.getAll());
  // }

  Widget build(BuildContext context) {
    return CustomScrollView(
      controller: controller,
      slivers: [
        CupertinoSliverNavigationBar(
          largeTitle: Text(ExtractPage.title),
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
                FutureBuilder(
                  future: _future,
                  builder: (context, snapshot) {
                    switch (snapshot.connectionState) {
                      case ConnectionState.none:
                      case ConnectionState.active:
                        break;
                      case ConnectionState.waiting:
                        return Text("CARREGANDO");
                      case ConnectionState.done:
                        if (snapshot.hasData) {
                          investments = snapshot.data;
                          return Container(
                            padding: EdgeInsets.only(left: 16, right: 16),
                            // child: _buildListView(context, snapshot.data));
                            child: _buildListView(context),
                          );
                        }
                    }
                    return Text("DEU RUIM");
                  },
                ),
              ]),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildListView(BuildContext context) {
    final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
    final defaultTheme = Theme.of(context).textTheme.bodyText2;

    return ListView.builder(
        padding: EdgeInsets.zero,
        physics: NeverScrollableScrollPhysics(),
        shrinkWrap: true,
        itemCount: investments.length,
        itemBuilder: (context, index) {
          StockInvestment item = investments[index];

          return CupertinoButton(
            padding: EdgeInsets.zero,
            onPressed: () => 1,
            // onPressed: () => showTransactionDetailsBottomSheet(context, item),
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
                          item.operation == "BUY"
                              ? Icons.trending_up
                              : Icons.trending_down,
                          color: item.operation == "BUY"
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
                                item.operation == "BUY" ? "Compra" : "Venda",
                                style: Theme.of(context)
                                    .textTheme
                                    .bodyText2
                                    .copyWith(fontSize: 12),
                              ),
                              SizedBox(
                                height: 8,
                              ),
                              Text(
                                item.ticker.replaceAll('.SA', ''),
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
                                formatter.format(item.date).capitalizeWords(),
                                style: Theme.of(context)
                                    .textTheme
                                    .bodyText2
                                    .copyWith(fontSize: 12),
                              ),
                              SizedBox(
                                height: 8,
                              ),
                              Text(
                                "${moneyFormatter.format(item.price * item.amount)}",
                                style: TextStyle(
                                    color: defaultTheme.color,
                                    fontWeight: FontWeight.w600,
                                    fontSize: defaultTheme.fontSize),
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
        });
  }
}
