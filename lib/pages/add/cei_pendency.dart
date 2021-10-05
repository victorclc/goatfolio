import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:goatfolio/vandelay/cubit/vandelay_cubit.dart';


class CeiPendency extends StatelessWidget {
  final Map<String, TextEditingController> tickerController = Map();

  CeiPendency({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      child: BlocBuilder<VandelayPendencyCubit, PendencyState>(
          builder: (context, state) {
        final cubit = BlocProvider.of<VandelayPendencyCubit>(context);
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
                      rows: cubit.divergences.entries.map<DataRow>(
                        (map) {
                          var controller = TextEditingController();
                          tickerController[map.key] = controller;
                          return DataRow(
                            cells: [
                              DataCell(
                                Text(map.key),
                              ),
                              DataCell(
                                Text('${map.value}'),
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
                  ElevatedButton(child: Text("ENVIAR"), onPressed: onSubmit),
                ],
              ),
            ),
          ),
        );
      }),
    );
  }

  void onSubmit() {
    tickerController.forEach(
      (ticker, controller) {
        if (controller.text.isNotEmpty) {
          final averagePrice = getDoubleFromMoneyFormat(controller.text);
          print(averagePrice);
        }
      },
    );
  }

  double getDoubleFromMoneyFormat(String formatted) {
    double value =
        double.parse(formatted.replaceAllMapped(RegExp(r'\D'), (match) {
      return '';
    }));
    return value / 100;
  }
}
