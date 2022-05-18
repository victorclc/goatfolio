import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/pages/add/stock_add.dart';
import 'package:goatfolio/pages/extract/cubit/extract_loader_cubit.dart';
import 'package:goatfolio/pages/extract/search/delegate.dart';
import 'package:goatfolio/pages/extract/widgets/dividend_extract_item.dart';
import 'package:goatfolio/pages/extract/widgets/stock_extract_item.dart';
import 'package:goatfolio/search/cupertino_search_delegate.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/investment/model/investment.dart';
import 'package:goatfolio/services/investment/model/stock_dividend.dart';
import 'package:goatfolio/services/investment/model/stock_investment.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:goatfolio/utils/extensions.dart';
import 'package:goatfolio/utils/focus.dart' as focus;
import 'package:goatfolio/utils/modal.dart' as modal;
import 'package:goatfolio/widgets/platform_aware_progress_indicator.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

class ExtractList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    throw UnimplementedError();
  }
}

class ExtractPage extends StatefulWidget {
  static const title = 'Extrato';
  static const icon = Icon(Icons.view_list);

  @override
  _ExtractPageStateOld createState() => _ExtractPageStateOld();
}

class _ExtractPageStateOld extends State<ExtractPage> {
  static const int limit = 15;
  final DateFormat monthFormatter = DateFormat('MMMM', 'pt_BR');
  TextEditingController searchController = TextEditingController();
  late StockInvestmentService stockService;
  List<Investment>? investments;
  late Future<List<Investment>?> _future;
  String? lastEvaluatedId;
  DateTime? lastEvaluatedDate;
  bool scrollLoading = false;
  late bool fetchingContent;
  bool hasFinished = false;

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    stockService = StockInvestmentService(userService);
    fetchingContent = true;
    _future = getInvestments();
  }

  bool scrollListener(ScrollNotification notification) {
    focus.unfocus(context);
    if (notification is ScrollEndNotification &&
        notification.metrics.extentAfter <= 100) {
      loadMoreInvestments();
    }
    return false;
  }

  Future<List<Investment>?> getInvestments() async {
    final data = await stockService.getInvestments(
        limit: limit,
        lastEvaluatedId: lastEvaluatedId,
        lastEvaluatedDate: lastEvaluatedDate);
    if (data != null) {
      lastEvaluatedId = data.lastEvaluatedId;
      lastEvaluatedDate = data.lastEvaluatedDate;
      if (lastEvaluatedId == null) {
        hasFinished = true;
      }
    }
    return data.investments;
  }

  Future<List<Investment>> getInvestmentsTicker(String ticker) async {
    return await stockService.getByTicker(ticker);
  }

  void loadMoreInvestments() async {
    if (hasFinished) return;
    setState(() {
      scrollLoading = true;
    });
    final data = await getInvestments();

    setState(() {
      scrollLoading = false;
      if (data != null) {
        investments!.addAll(data);
      }
    });
  }

  Future<void> onRefresh() async {
    if (!fetchingContent) {
      lastEvaluatedId = null;
      lastEvaluatedDate = null;
      hasFinished = false;
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
      placeHolderText: "Buscar ativo",
    );
  }

  Widget buildContent(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: scrollListener,
      child: GestureDetector(
        onTap: () => focus.unfocus(context),
        onVerticalDragStart: (_) => focus.unfocus(context),
        onPanStart: (_) => focus.unfocus(context),
        child: CustomScrollView(
          slivers: [
            CupertinoSliverNavigationBar(
              leading: Container(),
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
                                investments = snapshot.data as List<Investment>;
                                return buildExtractList(
                                    context, snapshot.data as List<Investment>);
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

  Widget buildExtractList(BuildContext context, List<Investment> investments) {
    DateTime? prevDateTime;
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
                  investment.date.month != prevDateTime!.month) {
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
                    if (investments[index] is StockInvestment)
                      StockExtractItem(
                        context,
                        investments[index] as StockInvestment,
                        onEditCb,
                        onDeleteCb,
                      ),
                    if (investments[index] is StockDividend)
                      DividendExtractItem(
                          context,
                          investments[index] as StockDividend,
                          onEditCb,
                          onDeleteCb)
                  ],
                );
              }
              prevDateTime = investment.date;
              if (investments[index] is StockInvestment)
                return StockExtractItem(
                  context,
                  investments[index] as StockInvestment,
                  onEditCb,
                  onDeleteCb,
                );
              if (investments[index] is StockDividend)
                return DividendExtractItem(
                    context,
                    investments[index] as StockDividend,
                    onEditCb,
                    onDeleteCb);
              return Container();
            },
          ),
        ),
        scrollLoading
            ? Platform.isIOS
                ? CupertinoActivityIndicator()
                : Center(child: CircularProgressIndicator())
            : Container(),
      ],
    );
  }

  void onEditCb(StockInvestment investment) async {
    await modal.showDraggableModalBottomSheet(
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
      investments!.remove(investment);
    });
    final data = await getInvestments();
    if (data != null && data.isNotEmpty) {
      setState(() {
        investments!.addAll(data);
      });
    }
  }
}

class _LoadingError extends StatelessWidget {
  final void Function() onPressed;

  const _LoadingError({Key? key, required this.onPressed}) : super(key: key);

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

// class _ExtractPageState extends State<ExtractPage> {
//   final DateFormat monthFormatter = DateFormat('MMMM', 'pt_BR');
//
//   void onEditCb(StockInvestment investment) async {
//     await modal.showDraggableModalBottomSheet(
//       context,
//       StockAdd.fromStockInvestment(
//         investment,
//         userService: Provider.of<UserService>(context, listen: false),
//       ),
//     );
//     setState(() {});
//   }
//
//   @override
//   Widget build(BuildContext context) {
//     return BlocBuilder<ExtractLoaderCubit, LoadingState>(
//       builder: (context, state) {
//         final cubit = BlocProvider.of<ExtractLoaderCubit>(context);
//         return buildSliver(
//             context,
//             cubit,
//             children: [
//               Builder(
//                 builder: (context) {
//                   switch (state) {
//                     case LoadingState.LOADING:
//                       return PlatformAwareProgressIndicator();
//                     case LoadingState.LOADED:
//                     case LoadingState.LOADED:
//                       return buildExtractList(context, cubit, cubit.investments);
//                     case LoadingState.ERROR:
//                     default:
//                       return _LoadingError(onPressed: cubit.refreshAll,);
//                   }
//                 },
//               )
//             ]
//         );
//       },
//     );
//   }
//
//   Widget buildEmptyExtractList() {
//     return Center(
//       child: Text(
//         "Nenhuma movimentação cadastrada",
//         style: CupertinoTheme
//             .of(context)
//             .textTheme
//             .textStyle,
//       ),
//     );
//   }
//
//   Widget buildExtractList(BuildContext context, ExtractLoaderCubit cubit,
//       List<Investment>? investments,) {
//     if (investments == null || investments.isEmpty) return buildEmptyExtractList();
//
//     DateTime? prevDateTime;
//
//     return Column(
//       children: [
//         Container(
//           padding: EdgeInsets.only(left: 16, right: 16),
//           child: ListView.builder(
//             padding: EdgeInsets.zero,
//             physics: NeverScrollableScrollPhysics(),
//             shrinkWrap: true,
//             itemCount: investments.length,
//             itemBuilder: (context, index) {
//               final investment = investments[index];
//               if (prevDateTime == null ||
//                   investment.date.month != prevDateTime!.month) {
//                 prevDateTime = investment.date;
//                 return Column(
//                   children: [
//                     Container(
//                       width: double.infinity,
//                       padding: EdgeInsets.only(bottom: 16),
//                       alignment: Alignment.centerLeft,
//                       child: Text(
//                         '${monthFormatter.format(investment.date)
//                             .capitalize()} de ${investment.date.year}',
//                         style: CupertinoTheme
//                             .of(context)
//                             .textTheme
//                             .navTitleTextStyle,
//                       ),
//                     ),
//                     if (investments[index] is StockInvestment)
//                       StockExtractItem(
//                         context,
//                         investments[index] as StockInvestment,
//                         onEditCb,
//                         cubit.deleteStock,
//                       )
//                   ],
//                 );
//               }
//               prevDateTime = investment.date;
//               if (investments[index] is StockInvestment)
//                 return StockExtractItem(
//                   context,
//                   investments[index] as StockInvestment,
//                   onEditCb,
//                   cubit.deleteStock,
//                 );
//               return Container();
//             },
//           ),
//         ),
//         cubit.state == LoadingState.UPDATING
//             ? PlatformAwareProgressIndicator()
//             : Container(),
//       ],
//     );
//   }
//
//
//   Widget buildSliver(BuildContext context,
//       ExtractLoaderCubit cubit,
//       {required List<Widget> children}) {
//     final widget = NotificationListener<ScrollNotification>(
//       onNotification: (notification) {
//         focus.unfocus(context);
//         if (notification is ScrollEndNotification &&
//             notification.metrics.extentAfter <= 100) {
//           cubit.loadNext();
//         }
//         return false;
//       },
//       child: GestureDetector(
//         onTap: () => focus.unfocus(context),
//         onVerticalDragStart: (_) => focus.unfocus(context),
//         onPanStart: (_) => focus.unfocus(context),
//         child: CustomScrollView(
//           slivers: [
//             CupertinoSliverNavigationBar(
//               leading: Container(),
//               heroTag: 'extractNavBar',
//               largeTitle: Text(ExtractPage.title),
//               backgroundColor:
//               CupertinoTheme
//                   .of(context)
//                   .scaffoldBackgroundColor,
//               trailing: IconButton(
//                 icon: Icon(CupertinoIcons.search),
//                 onPressed: () =>
//                     showCupertinoSearch(
//                       context: context,
//                       delegate: ExtractSearchDelegate(
//                         cubit.geAllByTicker,
//                         build, // todo mover aqui
//                       ),
//                       placeHolderText: "Buscar ativo",
//                     ),
//                 padding: EdgeInsets.zero,
//                 alignment: Alignment.centerRight,
//               ),
//             ),
//             if (Platform.isIOS)
//               CupertinoSliverRefreshControl(
//                 onRefresh: cubit.refreshAll,
//               ),
//             SliverSafeArea(
//               top: false,
//               sliver: SliverPadding(
//                 padding: EdgeInsets.symmetric(vertical: 12),
//                 sliver: SliverList(
//                   delegate: SliverChildListDelegate.fixed(children),
//                 ),
//               ),
//             ),
//           ],
//         ),
//       ),
//     );
//     if (Platform.isAndroid) {
//       return RefreshIndicator(
//         onRefresh: cubit.refreshAll,
//         child: widget,
//       );
//     }
//     return widget;
//   }
// }
