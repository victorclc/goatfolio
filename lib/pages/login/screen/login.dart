import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/constant/app.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/focus.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/animated_button.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';
import 'package:goatfolio/common/widget/preety_text_field.dart';
import 'package:goatfolio/pages/login/prompt/signin.dart';
import 'package:goatfolio/services/authentication/model/user.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';

class LoginPage extends StatelessWidget {
  final TextEditingController userController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final FocusNode emailNode = FocusNode();
  final FocusNode passwordNode = FocusNode();
  final UserService userService;

  final Function onLoggedOn;

  LoginPage({Key key, @required this.onLoggedOn, this.userService})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusUtils.unfocus(context),
      child: SafeArea(
        child: SingleChildScrollView(
          child: Container(
            padding: EdgeInsets.all(16),
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Image(
                    image: AssetImage(AppConstants.APP_LOGO),
                    height: 152,
                    width: 152,
                  ),
                ),
                PrettyTextField(
                  label: 'E-mail',
                  focusNode: emailNode,
                  controller: userController,
                  autoFillHints: [AutofillHints.email],
                  textInputType: TextInputType.emailAddress,
                ),
                PrettyTextField(
                  label: 'Senha',
                  hideText: true,
                  focusNode: passwordNode,
                  controller: passwordController,
                  autoFillHints: [AutofillHints.password],
                  textInputType: TextInputType.visiblePassword,
                ),
                Container(
                  alignment: Alignment.centerRight,
                  child: CupertinoButton(
                    padding: EdgeInsets.all(0),
                    child: Text("Esqueceu sua senha?"),
                    onPressed: () => _forgotPassword(context, userService),
                  ),
                ),
                SizedBox(
                  height: 16,
                ),
                Container(
                  width: double.infinity,
                  child: AnimatedButton(
                    onPressed: () => _onLoginSubmit(context, userService),
                    animatedText: "...",
                    normalText: "ENTRAR",
                    filled: true,
                  ),
                ),
                SizedBox(
                  height: 32,
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text("Não tem uma conta?  "),
                    CupertinoButton(
                      padding: EdgeInsets.all(0),
                      child: Text("Criar conta"),
                      onPressed: () => _onSigUpTap(context, userService),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _onLoginSubmit(BuildContext context, UserService userService) async {
    final String username = userController.text;
    final String password = passwordController.text;

    if (username.isEmpty || password.isEmpty) return;

    String message = "";

    try {
      await userService.login(username, password);
      print(await userService.getSessionToken());
      onLoggedOn(context, userService);
      return;
    } on CognitoClientException catch (e) {
      if (e.code == 'InvalidParameterException' ||
          e.code == 'NotAuthorizedException' ||
          e.code == 'UserNotFoundException' ||
          e.code == 'ResourceNotFoundException') {
        message = "Usuário ou senha incorretos";
        debugPrint(e.toString());
      } else if (e.code == 'NetworkError') {
        message = "Sem conexão com a internet";
      } else if (e.code == 'UserNotConfirmedException') {
        return await _confirmAccount(context, userService, username, password);
      }
    } catch (e) {
      debugPrint(e.toString());
      message = 'Ops. Aconteceu um erro';
    }
    await DialogUtils.showErrorDialog(context, message);
  }

  void _onSigUpTap(BuildContext context, UserService userService) async {
    await ModalUtils.showUnDismissibleModalBottomSheet(
        context,
        MultiPrompt(
          keepOpenOnError: true,
          promptRequests: [
            SignInEmailPrompt(),
            SignInNamePrompt(),
            SignInPasswordPrompt(),
            SignInPasswordConfirmationPrompt()
          ],
          onSubmit: (Map values) async =>
              await onSignUpSubmit(context, userService, values),
        ));
  }

  Future<void> onSignUpSubmit(
      BuildContext context, UserService userService, Map values) async {
    try {
      User user = await userService.signUp(values['email'], values['password'], attributes: {"given_name":values['name']});
      print(user);
      if (user != null) {
        print("CONFIRM ACCOUNT");
        await _confirmAccount(
            context, userService, values['email'], values['password']);
      }
    } on CognitoClientException catch (e) {
      if (e.name == "UsernameExistsException") {
        await DialogUtils.showErrorDialog(context, "E-mail ja cadastrado.");
      } else {
        debugPrint(e.toString());
      }
    }
  }

  Future<void> _confirmAccount(BuildContext context, UserService userService,
      String email, String password) async {
    await ModalUtils.showUnDismissibleModalBottomSheet(
        context,
        MultiPrompt(
          keepOpenOnError: true,
          promptRequests: [
            SignInEmailConfirmationPrompt(context, userService, email),
          ],
          onSubmit: (Map values) async => await onConfirmAccountSubmit(
              context, userService, email, password, values),
        ));
  }

  Future<void> _forgotPassword(
      BuildContext context, UserService userService) async {
    await ModalUtils.showUnDismissibleModalBottomSheet(
      context,
      MultiPrompt(
        promptRequests: [
          SignInForgotPasswordPrompt(),
        ],
        onSubmit: (Map values) async {
          try {
            await userService.forgotPassword(values['email']);
            await _confirmPassword(context, userService, values['email']);
          } on CognitoClientException catch (e) {
            if (e.name == "LimitExceededException") {
              await DialogUtils.showErrorDialog(context,
                  "Você excedeu o número de tentativas, volte mais tarde.");
            } else if (e.name == "CodeMismatchException") {
              await DialogUtils.showErrorDialog(
                  context, "Código de verificação inválido");
            }
            rethrow;
          }
        },
      ),
    );
  }

  Future<void> _confirmPassword(
      BuildContext context, UserService userService, String email) async {
    await ModalUtils.showUnDismissibleModalBottomSheet(
      context,
      MultiPrompt(
        promptRequests: [
          SignInEmailConfirmationForPasswordChangePrompt(context),
          SignInPasswordPrompt(),
          SignInPasswordConfirmationPrompt()
        ],
        onSubmit: (values) async {
          print("_confirmPassword onSubmit");
          await userService.confirmPassword(
              email, values['confirmationCode'], values['password']);
          await DialogUtils.showSuccessDialog(
              context, "Sua senha foi alterada com sucesso!");
        },
      ),
    );
  }

  Future<void> onConfirmAccountSubmit(
      BuildContext context,
      UserService userService,
      String email,
      String password,
      Map values) async {
    try {
      await userService.confirmAccount(email, values['confirmationCode']);
      userController.text = email;
      passwordController.text = password;
      _onLoginSubmit(context, userService);
    } on CognitoClientException catch (e) {
      if (e.name == "CodeMismatchException") {
        await DialogUtils.showErrorDialog(
            context, "Código de verificação inválido");
      }
      rethrow;
    }
  }
}
