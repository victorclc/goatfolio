import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/add/prompt/add_stock_prompt.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';
import 'package:goatfolio/common/widget/preety_text_field.dart';
import 'package:goatfolio/investment/model/stock.dart';
import 'package:goatfolio/investment/service/stock_investment_service.dart';
import 'package:goatfolio/investment/storage/stock_investment.dart';
import 'package:provider/provider.dart';

void goTInvestmentList(BuildContext context, bool buyOperation) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => InvestmentsList(
        buyOperation: buyOperation,
      ),
    ),
  );
}

class InvestmentsList extends StatefulWidget {
  final bool buyOperation;

  const InvestmentsList({Key key, @required this.buyOperation})
      : super(key: key);

  @override
  _InvestmentsListState createState() => _InvestmentsListState();
}

class _InvestmentsListState extends State<InvestmentsList> {
  StockInvestmentStorage storage;
  StockInvestmentService service;
  Future<List<String>> _future;

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    storage = StockInvestmentStorage();
    service = StockInvestmentService(userService);
    _future = storage.getDistinctTickers();
  }

  void onStockSubmit(Map values) async {
    print(values);
    final investment = StockInvestment(
      ticker: values['ticker'],
      amount: int.parse(values['amount']),
      price: double.parse(values['price']),
      date: DateTime.now(), //values['date'],
      costs: double.parse(values['costs']),
      broker: values['broker'],
      type: "STOCK",
      operation: widget.buyOperation ? "BUY" : "SELL",
    );
    try {
      print("DENTRO DO TRY");
      await service.addInvestment(investment);
    } catch (Exception) {
      await DialogUtils.showErrorDialog(
          context, "Erro ao adicionar operação, tente novamente.");
      return;
    }
    await DialogUtils.showSuccessDialog(
        context, "Operação adicionada com sucesso!");
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          previousPageTitle: "",
          middle: Text(widget.buyOperation ? "Compra" : "Venda"),
        ),
        child: SafeArea(
          child: Container(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: PrettyTextField(
                    label: 'Buscar',
                    suffixIcon: Icon(Icons.search),
                  ),
                ),
                SizedBox(
                  height: 8,
                ),
                Container(
                  decoration: BoxDecoration(
                    border: Border(
                      top: BorderSide(color: Colors.grey),
                      bottom: BorderSide(color: Colors.grey),
                    ),
                  ),
                  padding:
                      EdgeInsets.only(left: 16, right: 16, top: 8, bottom: 8),
                  width: double.infinity,
                  child: widget.buyOperation
                      ? CupertinoButton(
                          padding: EdgeInsets.all(0),
                          onPressed: () =>
                              ModalUtils.showUnDismissibleModalBottomSheet(
                                  context,
                                  MultiPrompt(
                                    onSubmit: onStockSubmit,
                                    promptRequests: [
                                      StockTickerPrompt(),
                                      StockAmountPrompt(),
                                      StockPricePrompt(),
                                      StockDatePrompt(),
                                      StockBrokerPrompt(),
                                      StockCostsPrompt(),
                                    ],
                                  )),
                          child: Row(
                            children: [
                              Icon(Icons.add_circle_outline),
                              Padding(
                                padding: const EdgeInsets.only(left: 16.0),
                                child: Text("Adicionar novo ativo"),
                              ),
                              Expanded(
                                child: Container(
                                    alignment: Alignment.centerRight,
                                    child: Icon(Icons.keyboard_arrow_right)),
                              )
                            ],
                          ),
                        )
                      : Container(),
                ),
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
                            print(snapshot.data);
                            final List<String> tickers = snapshot.data;
                            return Expanded(
                                child: ListView.builder(
                              itemCount: tickers.length,
                              itemBuilder: (context, index) {
                                return CupertinoButton(
                                  padding: EdgeInsets.all(0),
                                  onPressed: () => 1,
                                  child: Container(
                                    padding: EdgeInsets.all(16),
                                    decoration: BoxDecoration(
                                      border: Border(
                                        bottom: BorderSide(color: Colors.grey),
                                      ),
                                    ),
                                    child: Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          tickers[index],
                                          style: Theme.of(context)
                                              .textTheme
                                              .subtitle1,
                                        ),
                                        Icon(Icons
                                            .keyboard_arrow_right_outlined),
                                      ],
                                    ),
                                  ),
                                );
                              },
                            ));
                          }
                      }
                      return Container();
                    }),
              ],
            ),
          ),
        ));
  }
}
