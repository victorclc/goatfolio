import 'package:goatfolio/services/friends/model/user.dart';

class Friend {
  final User user;
  final DateTime date;

  Friend(this.user, this.date);

  Friend.fromJson(Map<String, dynamic> json)
      : date = DateTime.parse('${json['date']}'),
        user = User.fromJson(json['user']);
}
