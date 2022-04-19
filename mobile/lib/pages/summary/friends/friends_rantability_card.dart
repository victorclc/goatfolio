import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/pages/share/share_page.dart';
import 'package:goatfolio/services/friends/cubit/friends_rentability_cubit.dart';
import 'package:goatfolio/services/friends/model/friend_rentability.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:goatfolio/widgets/platform_aware_progress_indicator.dart';
import 'package:goatfolio/widgets/pressable_card.dart';

class FriendsRentabilityCard extends StatefulWidget {
  const FriendsRentabilityCard({Key? key}) : super(key: key);

  @override
  _FriendsRentabilityCardState createState() => _FriendsRentabilityCardState();
}

class _FriendsRentabilityCardState extends State<FriendsRentabilityCard> {
  @override
  void initState() {
    super.initState();
  }

  Widget buildTop(List<FriendRentability> rentability) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    int listSize = rentability.length > 3 ? 3 : rentability.length;
    List<Widget> list = [];
    list.add(
      Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Nome",
                style: textTheme.textStyle.copyWith(fontSize: 16),
              ),
              Text(
                "Hoje",
                style: textTheme.textStyle.copyWith(fontSize: 16),
              ),
            ],
          ),
          SizedBox(
            height: 8,
          )
        ],
      ),
    );
    for (int i = 0; i < listSize; i++) {
      FriendRentability friendRentability = rentability[i];
      list.add(Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Flexible(
            flex: 1,
            child: Text(
              friendRentability.user.name,
              style: textTheme.textStyle.copyWith(fontSize: 14),
              softWrap: false,
            ),
          ),
          // Text(moneyFormatter.format(stock.currentStockPrice)),
          Flexible(
            child: Text(
              percentFormatter
                  .format(friendRentability.summary.dayVariationPerc / 100),
              style: textTheme.textStyle
                  .copyWith(fontSize: 14, color: friendRentability.summary.dayVariationPerc >= 0 ? Colors.green: Colors.red),
            ),
          ),
        ],
      ));
      list.add(
        Divider(
          height: 16,
          color: Colors.grey,
        ),
      );
    }
    return Column(
      children: list,
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Container(
      width: double.infinity,
      height: 210,
      child: PressableCard(
        cardPadding: EdgeInsets.only(left: 16, right: 4, top: 0, bottom: 16),
        onPressed: () => goToSharePage(context),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Container(
                alignment: Alignment.centerLeft,
                child: Text(
                  "Amigos",
                  style: CupertinoTheme.of(context).textTheme.navTitleTextStyle,
                ),
              ),
              SizedBox(
                height: 16,
              ),
              BlocBuilder<FriendsRentabilityCubit, LoadingState>(
                builder: (context, loadingState) {
                  final cubit =
                      BlocProvider.of<FriendsRentabilityCubit>(context);
                  if (loadingState == LoadingState.LOADING &&
                      cubit.rentabilityList == null) {
                    return PlatformAwareProgressIndicator();
                  }
                  if (loadingState == LoadingState.LOADED ||
                      cubit.rentabilityList != null) {
                    final rentabilityCopy = [...cubit.rentabilityList!];
                    rentabilityCopy.sort((b, a) => a.summary.dayVariationPerc
                        .compareTo(b.summary.dayVariationPerc));

                    return buildTop(rentabilityCopy);
                  }
                  return Expanded(
                    child: Center(
                      child: Padding(
                        padding: EdgeInsets.only(bottom: 16),
                        child: Text("Erro ao carregar",
                            style: textTheme.textStyle, textAlign: TextAlign.center,),
                      ),
                    ),
                  );
                },
              )
              // CupertinoButton(child: Text("TESTE"), onPressed: () => print(1))
            ],
          ),
        ),
      ),
    );
  }
}
