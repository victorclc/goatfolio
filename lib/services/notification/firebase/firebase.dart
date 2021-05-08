import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/notification/client/notification.dart';

Future<void> initializeFirebaseNotifications() async {
  await Firebase.initializeApp();
  await FirebaseMessaging.instance.setForegroundNotificationPresentationOptions(
    alert: true, // Required to display a heads up notification
    badge: true,
    sound: true,
  );
}

Future<void> setupPushNotifications(UserService userService) async {
  await FirebaseMessaging.instance.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false,
    provisional: false,
    sound: true,
  );
  NotificationClient client = NotificationClient(userService);
  client.registerToken(await FirebaseMessaging.instance.getToken());
  FirebaseMessaging.instance.onTokenRefresh.listen((newToken) {
    client.registerToken(newToken);
  });
}
