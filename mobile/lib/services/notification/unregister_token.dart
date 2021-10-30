class UnRegisterTokenRequest {
  String token;

  UnRegisterTokenRequest(this.token);

  Map<String, dynamic> toJson() => {'token': token};
}
