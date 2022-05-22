import 'package:badges/badges.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/share/share_page.dart';
import 'package:goatfolio/widgets/pressable_card.dart';

class AnalysisPage extends StatefulWidget {
  static const title = 'Análises';
  static const icon = Icon(Icons.lightbulb_outline);

  const AnalysisPage({Key? key}) : super(key: key);

  @override
  State<AnalysisPage> createState() => _AnalysisPageState();
}

class _AnalysisPageState extends State<AnalysisPage> {
  @override
  Widget build(BuildContext context) {

    return  CustomScrollView(
      slivers: [
        CupertinoSliverNavigationBar(
          leading: Container(),
          heroTag: 'analysisNavBar',
          largeTitle: Text(AnalysisPage.title),
          backgroundColor:
          CupertinoTheme.of(context).scaffoldBackgroundColor,
          border: null,
        ),

        SliverSafeArea(
          top: false,
          sliver: SliverPadding(
            padding: EdgeInsets.symmetric(vertical: 12),
            sliver: SliverList(
              delegate: SliverChildListDelegate.fixed(
                [
                  AnalysisCard(
                    title: "Proventos",
                    description: "Análise de todos os proventos recebidos.",
                    onPressed: () => 1,

                  ),
                  AnalysisCard(
                    title: "Amigos",
                    description: "Compartilhe e acompanhe a rentabilidade de seus amigos.",
                    onPressed: () => goToSharePage(context),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );

  }
}

class AnalysisCard extends StatelessWidget {
  final String title;
  final String description;
  final Function() onPressed;
  final bool betaFlag = true;

  const AnalysisCard({
    Key? key,
    required this.title,
    required this.description,
    required this.onPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return PressableCard(
      cardPadding: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      onPressed: onPressed,
      child: Container(
        height: 120,
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: CupertinoTheme.of(context)
                      .textTheme
                      .textStyle
                      .copyWith(fontWeight: FontWeight.w500),
                ),
                Row(
                  children: [
                    if (betaFlag)
                      Badge(
                        toAnimate: false,
                        shape: BadgeShape.square,
                        badgeColor: Colors.red,
                        borderRadius: BorderRadius.circular(8),
                        badgeContent: Text('BETA', style: TextStyle(color: Colors.white, fontSize: 8)),
                      ),
                    Container(
                      padding: EdgeInsets.only(left: 16),
                      alignment: Alignment.center,
                      child: Icon(
                        Icons.arrow_forward_ios,
                        size: 14,
                        color: Colors.grey,
                      ),
                    ),
                  ],
                )
              ],
            ),
            SizedBox(
              height: 8,
            ),
            Divider(
              height: 1,
            ),
            SizedBox(
              height: 8,
            ),
            Text(description)
          ],
        ),
      ),
    );
  }
}
