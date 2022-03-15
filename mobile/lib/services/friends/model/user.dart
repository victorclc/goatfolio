

class User {
  final String sub;
  final String name;
  final String email;

  User(this.sub, this.name, this.email);

  User.fromJson(Map<String, dynamic> json)
      : sub = json['sub'],
        name = json['name'],
        email = json['email'];
}