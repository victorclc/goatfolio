import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/help/model/faq.dart';

void goToHelpPage(BuildContext context, Faq faq) {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => HelpPage(
        faq: faq,
      ),
    ),
  );
}

class HelpPage extends StatelessWidget {
  final Faq faq;

  const HelpPage({Key? key, required this.faq}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
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
          faq.description,
          style: TextStyle(color: textColor),
        ),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: buildContent(context),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text(faq.description),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    return SingleChildScrollView(
      child: Container(
        child: Column(
          children: faq.questions
              .map(
                (question) => ExpansionTile(
                  title: Text(question.question),
                  children: [
                    Container(
                      padding: EdgeInsets.only(left: 16, right: 16, bottom: 16),
                      alignment: Alignment.centerLeft,
                      child: Text(question.answer),
                    ),
                  ],
                ),
              )
              .toList(),
        ),
      ),
    );
  }
}
