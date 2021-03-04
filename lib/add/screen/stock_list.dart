import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/add/prompt/add_stock_prompt.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';
import 'package:goatfolio/common/widget/preety_text_field.dart';
import 'package:goatfolio/investment/storage/stock_investment.dart';

void goTInvestmentList(BuildContext context) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => InvestmentsList(),
    ),
  );
}

class InvestmentsList extends StatefulWidget {
  @override
  _InvestmentsListState createState() => _InvestmentsListState();
}

class _InvestmentsListState extends State<InvestmentsList> {
  StockInvestmentStorage storage;
  Future<List<String>> _future;

  @override
  void initState() {
    super.initState();
    storage = StockInvestmentStorage();
    _future = storage.getDistinctTickers();
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          previousPageTitle: "",
          middle: Text("Compra"),
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
                  child: CupertinoButton(
                    padding: EdgeInsets.all(0),
                    onPressed: () =>
                        ModalUtils.showUnDismissibleModalBottomSheet(
                            context,
                            MultiPrompt(
                              onSubmit: (maps) => print(maps),
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
                  ),
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
