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
  PortfolioClient client;
  StockInvestmentStorage storage;

  @override
  void initState() {
    super.initState();
    client = PortfolioClient(Provider.of<UserService>(context, listen: false));
    storage = StockInvestmentStorage();
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
                  future: storage.getAll(),
                  builder: (context, snapshot) {
                    switch (snapshot.connectionState) {
                      case ConnectionState.none:
                      case ConnectionState.active:
                        break;
                      case ConnectionState.waiting:
                        return Text("CARREGANDO");
                      case ConnectionState.done:
                        if (snapshot.hasData) {
                          return Container(
                              padding: EdgeInsets.only(left: 16, right: 16),
                              child: _buildListView(context, snapshot.data));
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

  Widget _buildListView(
      BuildContext context, List<StockInvestment> investments) {
    var sortedInvestments = investments
      ..sort((a, b) => b.date.compareTo(a.date));
    final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
    final defaultTheme = Theme.of(context).textTheme.bodyText2;

    return ListView.builder(
        padding: EdgeInsets.zero,
        physics: NeverScrollableScrollPhysics(),
        shrinkWrap: true,
        itemCount: sortedInvestments.length,
        itemBuilder: (context, index) {
          StockInvestment item = sortedInvestments[index];

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
