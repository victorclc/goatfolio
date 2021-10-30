class RegisterTokenRequest {
  String token;
  String oldToken;

  RegisterTokenRequest(this.token, this.oldToken);

  Map<String, dynamic> toJson() => {'token': token, 'old_token': oldToken};
}
