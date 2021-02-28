import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/investment/client/portfolio.dart';
import 'package:goatfolio/investment/model/stock.dart';
import 'package:goatfolio/investment/storage/stock_investment.dart';
import 'package:provider/provider.dart';

class ExtractPage extends StatefulWidget {
  static const title = 'Extrato';
  static const icon = Icon(Icons.view_list);

  @override
  _ExtractPageState createState() => _ExtractPageState();
}

class _ExtractPageState extends State<ExtractPage> {
  PortfolioClient client;

  @override
  void initState() {
    super.initState();
    client =
        PortfolioClient(Provider.of<UserService>(context, listen: false));
    StockInvestmentStorage();
    Future<List<StockInvestment>> investments = client.getInvestments();
  }

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

              ]),
            ),
          ),
        ),
      ],
    );
  }
}
