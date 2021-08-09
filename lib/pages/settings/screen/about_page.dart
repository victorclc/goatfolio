import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/helper/theme_helper.dart';
import 'package:goatfolio/common/util/navigator.dart';
import 'package:launch_review/launch_review.dart';
import 'package:package_info/package_info.dart';
import 'package:settings_ui/settings_ui.dart';
import 'package:url_launcher/url_launcher.dart';

void goToAboutPage(BuildContext context) {
  NavigatorUtils.push(
    context,
    (context) => AboutPage(),
  );
}

class AboutPage extends StatefulWidget {
  @override
  _AboutPageState createState() => _AboutPageState();
}

class _AboutPageState extends State<AboutPage> {
  String version;

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
          "Sobre",
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
      backgroundColor:
          CupertinoThemeHelper.currentBrightness(context) == Brightness.light
              ? Color(0xFFEFEFF4)
              : CupertinoTheme.of(context).scaffoldBackgroundColor,
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Sobre"),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return SafeArea(
      child: FutureBuilder(
        future: PackageInfo.fromPlatform(),
        builder: (context, snapshot) {
          print(snapshot);
          if (snapshot.connectionState == ConnectionState.done) {
            version = snapshot.data.version;
            return Container(
              alignment: Alignment.topCenter,
              padding: EdgeInsets.only(top: 32),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Column(
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(16),
                            child: Image(
                              image: AssetImage('images/icon/app-icon3.png'),
                              height: 75,
                              width: 75,
                            ),
                          ),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: EdgeInsets.only(left: 16),
                            child: Text(
                              '${snapshot.data.appName} ${snapshot.data.version}',
                              style: textTheme.textStyle,
                            ),
                          ),
                          Container(
                            padding: EdgeInsets.only(left: 16, top: 8),
                            child: Text(
                              'por Majesty Solutions',
                              style: textTheme.tabLabelTextStyle
                                  .copyWith(fontSize: 16),
                            ),
                          ),
                        ],
                      )
                    ],
                  ),
                  Expanded(
                    child: SingleChildScrollView(
                      child: SettingsList(
                        physics: NeverScrollableScrollPhysics(),
                        shrinkWrap: true,
                        sections: [
                          SettingsSection(
                            tiles: [
                              SettingsTile(
                                title: 'Instagram',
                                onPressed: (_) => _launchURL(
                                    "https://www.instagram.com/goatfolio/"),
                                // onPressed: goToThemePage,
                              ),
                              SettingsTile(
                                title: 'Avalie-nos',
                                onPressed: (_) async =>
                                    await LaunchReview.launch(),
                              ),
                              SettingsTile(
                                title: 'Termos de uso',
                                onPressed: (_) =>
                                    _launchURL("https://www.goatfolio.com.br/"),
                              ),
                              SettingsTile(
                                title: 'Política de privacidade',
                                onPressed: (_) =>
                                    _launchURL("https://www.goatfolio.com.br/"),
                              ),
                              SettingsTile(
                                title: 'Reportar um Bug',
                                onPressed: (_) => _launchBugReportEmail(),
                              ),
                              SettingsTile(
                                title: 'Requisição de funcionalidades',
                                onPressed: (_) => _launchFutureRequestEmail(),
                              ),
                              SettingsTile(
                                title: 'Contato',
                                onPressed: (_) => _launchContactEmail(),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            );
          }
          return CupertinoActivityIndicator();
        },
      ),
    );
  }

  Future<void> _launchURL(String url) async =>
      await canLaunch(url) ? await launch(url) : throw 'Could not launch $url';

  Future<void> _launchBugReportEmail() async {
    String url =
        'mailto:contato@goatfolio.com.br?subject=[$version]%20BUG%20Report';
    await canLaunch(url) ? await launch(url) : throw 'Could not launch $url';
  }

  Future<void> _launchFutureRequestEmail() async {
    String url =
        'mailto:contato@goatfolio.com.br?subject=[$version]%20Ideia%20de%20Funcionalidade';
    await canLaunch(url) ? await launch(url) : throw 'Could not launch $url';
  }

  Future<void> _launchContactEmail() async {
    String url = 'mailto:contato@goatfolio.com.br?subject=[$version]%20Contato';
    await canLaunch(url) ? await launch(url) : throw 'Could not launch $url';
  }
}
