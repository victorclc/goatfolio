import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:settings_ui/settings_ui.dart';

void goToNotificationsPage(BuildContext context) {
  Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => NotificationsPage(),
    ),
  );
}

class NotificationsPage extends StatefulWidget {
  @override
  _NotificationsPageeState createState() => _NotificationsPageeState();
}

class _NotificationsPageeState extends State<NotificationsPage> {
  bool switchValue = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Aparência"),
      ),
      child: SafeArea(
        child: SettingsList(
          sections: [
            SettingsSection(
              tiles: [
                SettingsTile.switchTile(
                  titleTextStyle: CupertinoTheme.of(context).textTheme.textStyle.copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                  title: 'Habilitar notificações',
                  onToggle: (value) {
                    setState(() {
                      switchValue = value;
                    });
                  },
                  switchValue: switchValue,
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
