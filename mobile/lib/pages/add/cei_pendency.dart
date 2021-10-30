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
    return CupertinoPageScaffold(
      child: BlocBuilder<StockDivergenceCubit, DivergenceState>(
          builder: (context, state) {
        final cubit = BlocProvider.of<StockDivergenceCubit>(context);
        final textTheme = CupertinoTheme.of(context).textTheme;

        return SingleChildScrollView(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: SafeArea(
              child: Column(
                children: [
                  Container(
                    padding: EdgeInsets.only(bottom: 16),
                    child: DataTable(
                      dividerThickness: 0.00001,
                      dataRowHeight: 48,
                      columns: [
                        DataColumn(
                          label: Text(
                            'Ativo',
                            style: textTheme.textStyle.copyWith(fontSize: 16),
                          ),
                        ),
                        DataColumn(
                          label: Text(
                            'Qtd. faltando',
                            style: textTheme.textStyle.copyWith(fontSize: 16),
                          ),
                          numeric: true,
                        ),
                        DataColumn(
                          label: Container(
                            width: 85,
                            child: Text(
                              'Preço médio',
                              style: textTheme.textStyle.copyWith(fontSize: 16),
                            ),
                          ),
                          numeric: true,
                        ),
                      ],
                      rows: cubit.divergences.map<DataRow>(
                        (map) {
                          TextEditingController controller;
                          if (tickerController.containsKey(map)) {
                            controller = tickerController[map]!;
                          } else {
                            controller = TextEditingController();
                            tickerController[map] = controller;
                          }
                          return DataRow(
                            cells: [
                              DataCell(
                                Text(map.ticker),
                              ),
                              DataCell(
                                Text('${map.missingAmount}'),
                              ),
                              DataCell(
                                CupertinoTextField(
                                  controller: controller,
                                  placeholder: 'R\$ 0,00 ',
                                  inputFormatters: [moneyInputFormatter],
                                  keyboardType: TextInputType.numberWithOptions(
                                    decimal: true,
                                  ),
                                ),
                                placeholder: true,
                              )
                            ],
                          );
                        },
                      ).toList(),
                    ),
                  ),
                  ElevatedButton(child: Text("ENVIAR"), onPressed: () => onSubmit(context, cubit)),
                ],
              ),
            ),
          ),
        );
      }),
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
