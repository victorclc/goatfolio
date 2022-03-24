import 'package:goatfolio/services/friends/model/friend.dart';

class FriendsList {
  final String subject;
  final List<Friend> friends;
  final List<Friend> requests;
  final List<Friend> invites;

  FriendsList(this.subject, this.friends, this.requests, this.invites);

  bool isEmpty() => friends.isEmpty && requests.isEmpty && invites.isEmpty;

  FriendsList.fromJson(Map<String, dynamic> json)
      : subject = json['subject'],
        friends = json['friends']
            .map<Friend>((json) => Friend.fromJson(json))
            .toList(),
        requests = json['requests']
            .map<Friend>((json) => Friend.fromJson(json))
            .toList(),
        invites = json['invites']
            .map<Friend>((json) => Friend.fromJson(json))
            .toList();
}
