import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/helper/theme_helper.dart';
import 'package:launch_review/launch_review.dart';
import 'package:package_info/package_info.dart';
import 'package:settings_ui/settings_ui.dart';
import 'package:url_launcher/url_launcher.dart';

void goToAboutPage(BuildContext context) {
  Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => AboutPage(),
    ),
  );
}

class AboutPage extends StatefulWidget {
  @override
  _AboutPageState createState() => _AboutPageState();
}

class _AboutPageState extends State<AboutPage> {
  String version;
  final String _contactUrl =
      'mailto:contato@goatfolio.com.br?subject=Teste&body=Isso%20eh%20uma%20mensagem%20de%20teste';

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
      backgroundColor: CupertinoThemeHelper.currentBrightness(context) == Brightness.light
          ? Color(0xFFEFEFF4)
          : CupertinoTheme.of(context).scaffoldBackgroundColor,
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Sobre"),
      ),
      child: SafeArea(
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
                                'por Victor Corte',
                                style: textTheme.tabLabelTextStyle
                                    .copyWith(fontSize: 16),
                              ),
                            ),
                          ],
                        )
                      ],
                    ),
                    SizedBox(
                      height: 32,
                    ),
                    Expanded(
                      child: SingleChildScrollView(
                        child: SettingsList(
                          backgroundColor: Platform.isAndroid
                              ? CupertinoTheme.of(context)
                                  .scaffoldBackgroundColor
                              : null,
                          physics: NeverScrollableScrollPhysics(),
                          shrinkWrap: true,
                          sections: [
                            SettingsSection(
                              tiles: [
                                SettingsTile(
                                  titleTextStyle: CupertinoTheme.of(context)
                                      .textTheme
                                      .textStyle
                                      .copyWith(
                                          fontWeight: FontWeight.normal,
                                          fontSize: 16),
                                  title: 'Instagram',
                                  onPressed: (_) => _launchURL(
                                      "https://www.instagram.com/goatfolio/"),
                                  // onPressed: goToThemePage,
                                ),
                                SettingsTile(
                                  titleTextStyle: CupertinoTheme.of(context)
                                      .textTheme
                                      .textStyle
                                      .copyWith(
                                          fontWeight: FontWeight.normal,
                                          fontSize: 16),
                                  title: 'Avalie-nos',
                                  onPressed: (_) async =>
                                      await LaunchReview.launch(),
                                ),
                                SettingsTile(
                                  titleTextStyle: CupertinoTheme.of(context)
                                      .textTheme
                                      .textStyle
                                      .copyWith(
                                          fontWeight: FontWeight.normal,
                                          fontSize: 16),
                                  title: 'Termos de uso',
                                  onPressed: (_) => _launchURL(
                                      "https://www.goatfolio.com.br/"),
                                ),
                                SettingsTile(
                                  titleTextStyle: CupertinoTheme.of(context)
                                      .textTheme
                                      .textStyle
                                      .copyWith(
                                          fontWeight: FontWeight.normal,
                                          fontSize: 16),
                                  title: 'Política de privacidade',
                                  onPressed: (_) => _launchURL(
                                      "https://www.goatfolio.com.br/"),
                                ),
                                SettingsTile(
                                  titleTextStyle: CupertinoTheme.of(context)
                                      .textTheme
                                      .textStyle
                                      .copyWith(
                                          fontWeight: FontWeight.normal,
                                          fontSize: 16),
                                  title: 'Reportar um Bug',
                                  onPressed: (_) => _launchBugReportEmail(),
                                ),
                                SettingsTile(
                                  titleTextStyle: CupertinoTheme.of(context)
                                      .textTheme
                                      .textStyle
                                      .copyWith(
                                          fontWeight: FontWeight.normal,
                                          fontSize: 16),
                                  title: 'Requisição de funcionalidades',
                                  onPressed: (_) => _launchFutureRequestEmail(),
                                ),
                                SettingsTile(
                                  titleTextStyle: CupertinoTheme.of(context)
                                      .textTheme
                                      .textStyle
                                      .copyWith(
                                          fontWeight: FontWeight.normal,
                                          fontSize: 16),
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
            return Center(child: CupertinoActivityIndicator());
          },
        ),
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
