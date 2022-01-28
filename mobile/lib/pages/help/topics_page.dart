import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/help/help_page.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/help/client/client.dart';
import 'package:goatfolio/services/help/model/faq.dart';
import 'package:goatfolio/widgets/loading_error.dart';
import 'package:goatfolio/widgets/platform_aware_progress_indicator.dart';
import 'package:settings_ui/settings_ui.dart';

void goToFaqTopicsPage(BuildContext context, UserService userService) {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => FaqTopicsPage(
        userService: userService,
      ),
    ),
  );
}

class FaqTopicsPage extends StatefulWidget {
  final UserService userService;

  const FaqTopicsPage({Key? key, required this.userService}) : super(key: key);

  @override
  _FaqTopicsPageState createState() => _FaqTopicsPageState();
}

class _FaqTopicsPageState extends State<FaqTopicsPage> {
  late HelpClient client;
  late Future<List<Faq>> _future;

  @override
  void initState() {
    client = HelpClient(widget.userService);
    _future = client.getFaq();
    super.initState();
  }


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
          "FAQ",
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
        middle: Text("FAQ"),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return FutureBuilder(
      future: _future,
      builder: (context, snapshot) {
        switch (snapshot.connectionState) {
          case ConnectionState.none:
          case ConnectionState.active:
            break;
          case ConnectionState.waiting:
            return PlatformAwareProgressIndicator();
          case ConnectionState.done:
            if (!snapshot.hasData) {
              return Column(
                children: [
                  SizedBox(
                    height: 240,
                    child: Center(
                      child: Text(
                        "Nenhum dado encontrado.",
                        style: textTheme.textStyle,
                      ),
                    ),
                  ),
                ],
              );
            }
            List<Faq> faqs = snapshot.data! as List<Faq>;

            return SettingsList(
              sections: [
                SettingsSection(
                  tiles: faqs
                      .map(
                        (faq) => SettingsTile(
                          title: faq.topic,
                          iosLikeTile: true,
                          onPressed: (context) => goToHelpPage(context, faq),
                        ),
                      )
                      .toList(),
                ),
              ],
            );
        }
        return LoadingError(
          onRefreshPressed: () => _future = client.getFaq(),
        );
      },
    );
  }
}
