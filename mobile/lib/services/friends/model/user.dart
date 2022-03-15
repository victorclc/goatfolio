

class FriendUser {
  final String sub;
  final String name;
  final String email;

  FriendUser(this.sub, this.name, this.email);

  FriendUser.fromJson(Map<String, dynamic> json)
      : sub = json['sub'],
        name = json['name'],
        email = json['email'];

  Map<String, dynamic> toJson() => {
    'sub': sub,
    'name': name,
    'email': email,
  };
}