import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/pages/login/cubit/exceptions.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/authentication/user.dart';

class AuthenticationCubit extends Cubit<LoadingState> {
  late final UserService userService;

  AuthenticationCubit() : super(LoadingState.IDLE);

  void login(String username, String password) async {
    if (username.isEmpty || password.isEmpty) return;
    emit(LoadingState.LOADING);
    try {
      await this.userService.login(username, password);
      emit(LoadingState.LOADED);
    } on CognitoClientException catch (e) {
      if (e.code == 'InvalidParameterException' ||
          e.code == 'NotAuthorizedException' ||
          e.code == 'UserNotFoundException' ||
          e.code == 'ResourceNotFoundException') {
        emit(LoadingState.ERROR);
        throw new InvalidUsernameOrPasswordException();
      } else if (e.code == 'NetworkError') {
        throw NetworkErrorException();
      } else if (e.code == 'UserNotConfirmedException') {
        emit(LoadingState.ERROR);
        throw UserNotConfirmedException();
      }
    } catch (e) {
      emit(LoadingState.ERROR);
      throw UnknownErrorException();
    }
  }

  Future<User?> signUp(String name, String email, String password) async {
    try {
      emit(LoadingState.LOADING);
      User user = await userService.signUp(
        email,
        password,
        attributes: {"given_name": name},
      );
      emit(LoadingState.LOADED);
      return user;
    } on CognitoClientException catch (e) {
      if (e.name == "UsernameExistsException") {
        emit(LoadingState.ERROR);
        throw UsernameAlreadyExistsException();
      }
    } catch (e) {
      // TODO PUT LOGS HERE
      emit(LoadingState.ERROR);
      throw UnknownErrorException();
    }
  }

  void confirmAccount(String username, String confirmationCode) async {
    emit(LoadingState.LOADING);
    try {
      await userService.confirmAccount(username, confirmationCode);
      emit(LoadingState.LOADED);
    } on CognitoClientException catch (e) {
      emit(LoadingState.ERROR);
      if (e.name == "CodeMismatchException") {
        throw CodeMismatchException();
      }
    } catch (e) {
      emit(LoadingState.ERROR);
      throw UnknownErrorException();
    }
  }

  void forgotPassword(String username) async {
    emit(LoadingState.LOADING);
    try {
      await userService.forgotPassword(username);
      emit(LoadingState.LOADED);
    } on CognitoClientException catch (e) {
      emit(LoadingState.ERROR);
      if (e.name == "LimitExceededException") {
        throw LimitExceededException();
      } else if (e.name == "CodeMismatchException") {
        throw CodeMismatchException();
      }
    } catch (e) {
      emit(LoadingState.ERROR);
      throw UnknownErrorException();
    }
  }

  void confirmPassword(
      String username, String confirmationCode, newPassword) async {
    emit(LoadingState.LOADING);
    try {
      await userService.confirmPassword(
          username, confirmationCode, newPassword);
      emit(LoadingState.LOADED);
    } catch (e) {
      emit(LoadingState.ERROR);
      throw UnknownErrorException();
    }
  }
}
