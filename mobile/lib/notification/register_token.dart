class RegisterTokenRequest {
  String token;


  RegisterTokenRequest(this.token);

  Map<String, dynamic> toJson() => {
        'token': token,
      };
}
