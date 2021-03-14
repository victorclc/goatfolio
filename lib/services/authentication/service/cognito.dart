import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/authentication/model/user.dart';
import 'package:goatfolio/services/authentication/storage/session.dart';
import 'package:shared_preferences/shared_preferences.dart';

class UserService {
  final String cognitoUserPoolId;
  final String cognitoClientId;
  final String cognitoIdentityPoolId;
  CognitoUserPool _userPool;
  CognitoUser _cognitoUser;
  CognitoUserSession _session;

  UserService(this.cognitoUserPoolId, this.cognitoClientId,
      this.cognitoIdentityPoolId) {
    _userPool = CognitoUserPool(cognitoUserPoolId, cognitoClientId);
  }

  CognitoCredentials credentials;

  /// Initiate user session from local storage if present
  Future<bool> init() async {
    final prefs = await SharedPreferences.getInstance().catchError((onError) {
      debugPrint(onError);
    });
    final storage = SessionStorage(prefs);

    _userPool.storage = storage;
    _cognitoUser = await _userPool.getCurrentUser();

    if (_cognitoUser == null) {
      return false;
    }
    _session = await _cognitoUser.getSession();

    return _session.isValid();
  }

  /// Get existing user from session with his/her attributes
  Future<User> getCurrentUser() async {
    if (_cognitoUser == null || _session == null) {
      return null;
    }
    if (!_session.isValid()) {
      return null;
    }
    final attributes = await _cognitoUser.getUserAttributes();
    if (attributes == null) {
      return null;
    }
    final user = User.fromUserAttributes(attributes);
    user.hasAccess = true;
    return user;
  }

  /// Retrieve user credentials -- for use with other AWS services
  Future<CognitoCredentials> getCredentials() async {
    if (_cognitoUser == null || _session == null) {
      return null;
    }
    credentials = CognitoCredentials(cognitoIdentityPoolId, _userPool);
    await credentials.getAwsCredentials(_session.getIdToken().getJwtToken());
    return credentials;
  }

  /// Login user
  Future<User> login(String email, String password) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _userPool.storage);

    final authDetails = AuthenticationDetails(
      username: email,
      password: password,
    );

    _session = await _cognitoUser.authenticateUser(authDetails);

    if (_session != null && !_session.isValid()) {
      return null;
    }

    final attributes = await _cognitoUser.getUserAttributes();
    final user = User.fromUserAttributes(attributes);
    user.confirmed = true;
    user.hasAccess = true;

    return user;
  }

  /// Confirm user's account with confirmation code sent to email
  Future<bool> confirmAccount(String username, String confirmationCode) async {
    _cognitoUser = CognitoUser(username, _userPool, storage: _userPool.storage);

    return await _cognitoUser.confirmRegistration(confirmationCode);
  }

  /// Resend confirmation code to user's email
  Future<void> resendConfirmationCode(String email) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _userPool.storage);
    await _cognitoUser.resendConfirmationCode();
  }

  Future<void> forgotPassword(String email) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _userPool.storage);
    await _cognitoUser.forgotPassword();
  }

  Future<void> confirmPassword(
      String email, confirmationCode, newPassword) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _userPool.storage);
    await _cognitoUser.confirmPassword(confirmationCode, newPassword);
  }

  Future<void> deleteUser() async {
    if (credentials != null) {
      await credentials.resetAwsCredentials();
    }
    if (_cognitoUser != null) {
      return _cognitoUser.deleteUser();
    }
  }

  /// Check if user's current session is valid
  bool checkAuthenticated() {
    if (_cognitoUser == null || _session == null) {
      return false;
    }
    return _session.isValid();
  }

  /// Sign user
  Future<User> signUp(String email, String password,
      {Map<String, String> attributes}) async {
    CognitoUserPoolData data;
    // final userAttributes = [
    //   AttributeArg(name: 'email', value: email),
    // ];
    data = await _userPool.signUp(
      email,
      password,
    );
    debugPrint("data returned by signUp ${data}");

    final user = User();
    user.username = email;
    user.confirmed = data.userConfirmed;

    return user;
  }

  Future<void> signOut() async {
    if (credentials != null) {
      await credentials.resetAwsCredentials();
    }
    if (_cognitoUser != null) {
      return _cognitoUser.signOut();
    }
  }

  Future<String> getSessionToken() async {
    if (!_session.isValid()) {
      _session = await _cognitoUser.getSession();
    }

    return _session.getIdToken().getJwtToken();
  }
}