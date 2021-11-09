import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/services/stock/divergence_model.dart';
import 'package:goatfolio/services/stock/stock_divergence_cubit.dart';
import 'package:goatfolio/utils/formatters.dart';

class CeiPendency extends StatelessWidget {
  final Map<Divergence, TextEditingController> tickerController = Map();

  CeiPendency({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return buildIos(context);

    // return buildAndroid(context);
  }

  Widget buildAndroid(BuildContext context) {
    final textColor =
        CupertinoTheme.of(context).textTheme.navTitleTextStyle.color;
    return Scaffold(
      appBar: AppBar(
        leading: BackButton(
          color: textColor,
        ),
        title: Text(
          "Pêndencias",
          style: TextStyle(color: textColor),
        ),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: buildContent(context),
    );
  }

  Widget buildIos(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    final cubit = BlocProvider.of<StockDivergenceCubit>(context);
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        border: null,
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        leading: CupertinoButton(
          padding: EdgeInsets.all(0),
          child: Align(
            alignment: AlignmentDirectional.centerStart,
            widthFactor: 1.0,
            child: Text(
              'Cancelar',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        middle: Text(
          "Pêndencias",
          style: textTheme.navTitleTextStyle,
        ),
        // trailing: CupertinoButton(
        //   padding: EdgeInsets.all(0),
        //   child: Align(
        //     alignment: AlignmentDirectional.centerStart,
        //     widthFactor: 1.0,
        //     child: Text(
        //       'Seguinte',
        //       maxLines: 1,
        //       overflow: TextOverflow.ellipsis,
        //     ),
        //   ),
        //   onPressed: () => onSubmit(context, cubit),
        // ),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    return BlocBuilder<StockDivergenceCubit, DivergenceState>(
      builder: (context, state) {
        final cubit = BlocProvider.of<StockDivergenceCubit>(context);
        final textTheme = CupertinoTheme.of(context).textTheme;

        return SingleChildScrollView(
          child: Column(
            children: [
              Column(
                children: cubit.divergences.map<ExpansionTile>((map) {
                  TextEditingController controller;
                  if (tickerController.containsKey(map)) {
                    controller = tickerController[map]!;
                  } else {
                    controller = TextEditingController();
                    tickerController[map] = controller;
                  }

                  return ExpansionTile(
                    initiallyExpanded: true,
                    title: Text(map.ticker),
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(
                          left: 16.0,
                          right: 16,
                          bottom: 4,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text("Quantidade esperada"),
                            Text("${map.expectedAmount}"),
                          ],
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.only(
                          left: 16.0,
                          right: 16,
                          bottom: 16,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text("Quantidade na carteira"),
                            Text("${map.actualAmount}")
                          ],
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.only(
                          left: 16.0,
                          right: 16,
                          bottom: 16,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Flexible(flex: 2, child: Text("Preço médio")),
                            Flexible(
                              flex: 1,
                              child: CupertinoTextField(
                                controller: controller,
                                placeholder: 'R\$ 0,00 ',
                                inputFormatters: [moneyInputFormatter],
                                keyboardType: TextInputType.numberWithOptions(
                                  decimal: true,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                }).toList(),
              ),
              SizedBox(height: 16),
              ElevatedButton(
                child: Text("ENVIAR"),
                onPressed: () => onSubmit(context, cubit),
              ),
              SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  void onSubmit(BuildContext context, StockDivergenceCubit cubit) {
    tickerController.forEach(
      (divergence, controller) {
        if (controller.text.isNotEmpty) {
          final averagePrice = getDoubleFromMoneyFormat(controller.text);
          cubit.resolveDivergence(divergence, averagePrice);
        }
      },
    );
    Navigator.pop(context);
  }

  double getDoubleFromMoneyFormat(String formatted) {
    double value =
        double.parse(formatted.replaceAllMapped(RegExp(r'\D'), (match) {
      return '';
    }));
    return value / 100;
  }
}
