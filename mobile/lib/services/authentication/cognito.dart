import 'dart:async';
import 'dart:convert';

import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:f_logs/f_logs.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/flavors.dart';
import 'package:goatfolio/services/authentication/session.dart';
import 'package:goatfolio/services/authentication/user.dart';
import 'package:http/http.dart';

import 'package:shared_preferences/shared_preferences.dart';
import 'package:webview_flutter/webview_flutter.dart';

class UserService {
  final String cognitoUserPoolId;
  final String cognitoClientId;
  final String cognitoIdentityPoolId;
  late CognitoUserPool _userPool;
  CognitoUser? _cognitoUser;
  CognitoUserSession? _session;
  CognitoCredentials? credentials;

  UserService(this.cognitoUserPoolId, this.cognitoClientId,
      this.cognitoIdentityPoolId) {
    _userPool = CognitoUserPool(cognitoUserPoolId, cognitoClientId);
  }


  /// Initiate user session from local storage if present
  Future<bool> init() async {
    final prefs = await SharedPreferences.getInstance().catchError((onError) {
      FLog.error(text: onError);
    });
    final storage = SessionStorage(prefs);

    _userPool.storage = storage;
    _cognitoUser = await _userPool.getCurrentUser();
    if (_cognitoUser == null) {
      return false;
    }
    _session = await _cognitoUser!.getSession();

    return _session!.isValid();
  }

  /// Get existing user from session with his/her attributes
  Future<User?> getCurrentUser() async {
    if (_cognitoUser == null || _session == null) {
      return null;
    }
    if (!_session!.isValid()) {
      return null;
    }
    final attributes = await _cognitoUser!.getUserAttributes();
    if (attributes == null) {
      return null;
    }
    final user = User.fromUserAttributes(attributes);
    user.hasAccess = true;
    return user;
  }

  /// Retrieve user credentials -- for use with other AWS services
  Future<CognitoCredentials?> getCredentials() async {
    if (_cognitoUser == null || _session == null) {
      return null;
    }
    credentials = CognitoCredentials(cognitoIdentityPoolId, _userPool);
    await credentials!.getAwsCredentials(_session!.getIdToken().getJwtToken());
    return credentials;
  }

  /// Login user
  Future<User?> login(String email, String password) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _userPool.storage);

    final authDetails = AuthenticationDetails(
      username: email,
      password: password,
    );

    _session = await _cognitoUser!.authenticateUser(authDetails);

    if (_session != null && !_session!.isValid()) {
      return null;
    }

    final attributes = await _cognitoUser!.getUserAttributes();
    final user = User.fromUserAttributes(attributes!);

    _userPool.storage.setItem(
        'CognitoIdentityServiceProvider.$cognitoClientId.LastAuthUser',
        user.email);

    user.confirmed = true;
    user.hasAccess = true;

    return user;
  }

  /// Confirm user's account with confirmation code sent to email
  Future<bool> confirmAccount(String username, String confirmationCode) async {
    _cognitoUser = CognitoUser(username, _userPool, storage: _userPool.storage);

    return await _cognitoUser!.confirmRegistration(confirmationCode);
  }

  /// Resend confirmation code to user's email
  Future<void> resendConfirmationCode(String email) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _userPool.storage);
    await _cognitoUser!.resendConfirmationCode();
  }

  Future<void> forgotPassword(String email) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _userPool.storage);
    await _cognitoUser!.forgotPassword();
  }

  Future<void> confirmPassword(String email, confirmationCode,
      newPassword) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _userPool.storage);
    await _cognitoUser!.confirmPassword(confirmationCode, newPassword);
  }

  Future<void> deleteUser() async {
    if (credentials != null) {
      await credentials!.resetAwsCredentials();
    }
    if (_cognitoUser != null) {
      _cognitoUser!.deleteUser();
    }
  }

  /// Check if user's current session is valid
  bool checkAuthenticated() {
    if (_cognitoUser == null || _session == null) {
      return false;
    }
    return _session!.isValid();
  }

  /// Sign user
  Future<User> signUp(String email, String password,
      {required Map<String, String> attributes}) async {
    final List<AttributeArg> userAttributes = [];
    attributes.forEach((key, value) {
      userAttributes.add(AttributeArg(name: key, value: value));
    });
    CognitoUserPoolData data = await _userPool.signUp(
      email,
      password,
      userAttributes: userAttributes
    );

    final user = User();
    user.username = email;
    user.confirmed = data.userConfirmed!;

    return user;
  }

  Future<void> signOut() async {
    if (credentials != null) {
      await credentials!.resetAwsCredentials();
    }
    if (_cognitoUser != null) {
      await _userPool.storage.removeItem(
          'CognitoIdentityServiceProvider.$cognitoClientId.LastAuthUser');
      return _cognitoUser!.signOut();
    }
  }

  Future<String?> getSessionToken() async {
    if (!_session!.isValid()) {
      _session = await _cognitoUser!.getSession();
    }

    return _session!.getIdToken().getJwtToken();
  }

  final Completer<WebViewController> _webViewController = Completer<WebViewController>();
  Widget getWebView() {
    var url = "https://goatfolio-dev.auth.sa-east-1" +
        ".amazoncognito.com/oauth2/authorize?identity_provider=SignInWithApple&redirect_uri=" +
        "https://myapp/&response_type=CODE&client_id=${F.cognitoFederatedClientId}" +
        "&scope=email%20openid%20aws.cognito.signin.user.admin";
    return
      WebView(
        initialUrl: url,
        userAgent: 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Mobile Safari/537.36',
        javascriptMode: JavascriptMode.unrestricted,
        onWebViewCreated: (WebViewController webViewController) {
          _webViewController.complete(webViewController);
        },
        navigationDelegate: (NavigationRequest request) {
          if (request.url.startsWith("myapp://?code=")) {
            String code = request.url.substring("https://myapp/?code=".length);
            signUserInWithAuthCode(code);
            return NavigationDecision.prevent;
          }

          return NavigationDecision.navigate;
        },
        gestureNavigationEnabled: true,
      );
  }

  Future signUserInWithAuthCode(String authCode) async {
    String url = "https://goatfolio-dev.auth.sa-east-1" +
        ".amazoncognito.com/oauth2/token?grant_type=authorization_code&client_id=" +
        "${F.cognitoFederatedClientId}&code=" + authCode + "&redirect_uri=myapp://";
    final response = await new Client().post(Uri.parse(url), body: {}, headers: {'Content-Type': 'application/x-www-form-urlencoded'});
    if (response.statusCode != 200) {
      throw Exception("Received bad status code from Cognito for auth code:" +
          response.statusCode.toString() + "; body: " + response.body);
    }

    final tokenData = json.decode(response.body);

    final idToken = CognitoIdToken(tokenData['id_token']);
    final accessToken = CognitoAccessToken(tokenData['access_token']);
    final refreshToken = CognitoRefreshToken(tokenData['refresh_token']);
    final session = CognitoUserSession(idToken, accessToken, refreshToken: refreshToken);
    final user = CognitoUser(null, _userPool, signInUserSession: session);

    // NOTE: in order to get the email from the list of user attributes, make sure you select email in the list of
    // attributes in Cognito and map it to the email field in the identity provider.
    final attributes = await user.getUserAttributes();
    for (CognitoUserAttribute attribute in attributes!) {
      if (attribute.getName() == "email") {
        user.username = attribute.getValue();
        break;
      }
    }

    return user;
  }

}