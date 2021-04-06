import 'package:flutter/cupertino.dart';
import 'package:package_info/package_info.dart';

void goToAboutPage(BuildContext context) {
  Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => AboutPage(),
    ),
  );
}

class AboutPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        previousPageTitle: "",
        middle: Text("Sobre"),
      ),
      child: SafeArea(
        child: FutureBuilder(
            future: PackageInfo.fromPlatform(),
            builder: (context, snapshot) {
              print(snapshot);
              if (snapshot.connectionState == ConnectionState.done) {
                return Container(
                  alignment: Alignment.topCenter,
                  padding: EdgeInsets.all(32),
                  child: Row(
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
                          )
                        ],
                      )
                    ],
                  ),
                );
              }
              return CupertinoActivityIndicator();
            }),
      ),
    );
  }
}
