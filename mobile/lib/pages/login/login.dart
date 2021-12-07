import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:f_logs/f_logs.dart';
import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/flavors.dart';

import 'package:goatfolio/pages/login/signin_prompts.dart';
import 'package:goatfolio/pages/login/terms_acceptance.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/authentication/user.dart';
import 'package:goatfolio/theme/helper.dart' as theme;
import 'package:goatfolio/utils/dialog.dart' as dialog;
import 'package:goatfolio/utils/modal.dart' as modal;
import 'package:goatfolio/widgets/animated_button.dart';
import 'package:goatfolio/widgets/multi_prompt.dart';
import 'package:goatfolio/widgets/preety_text_field.dart';
import 'package:goatfolio/widgets/remove_focus_detector.dart';


class LoginPage extends StatelessWidget {
  final TextEditingController userController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final FocusNode emailNode = FocusNode();
  final FocusNode passwordNode = FocusNode();
  final UserService userService;

  final Function onLoggedOn;

  LoginPage({Key? key, required this.onLoggedOn, required this.userService})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return RemoveFocusDetector(
      child: SafeArea(
        child: Container(
          padding: EdgeInsets.all(16),
          child: Column(
            children: [
              Expanded(child: this.userService.getWebView())
              // Padding(
              //   padding: const EdgeInsets.all(16.0),
              //   child: Image(
              //     color: theme.isDarkMode(context)
              //         ? Colors.grey
              //         : null,
              //     image: AssetImage(F.appLogo),
              //     height: 152,
              //     width: 152,
              //   ),
              // ),
              // PrettyTextField(
              //   label: 'E-mail',
              //   focusNode: emailNode,
              //   controller: userController,
              //   autoFillHints: [AutofillHints.email],
              //   textInputType: TextInputType.emailAddress,
              // ),
              // PrettyTextField(
              //   label: 'Senha',
              //   hideText: true,
              //   focusNode: passwordNode,
              //   controller: passwordController,
              //   autoFillHints: [AutofillHints.password],
              //   textInputType: TextInputType.visiblePassword,
              // ),
              // Container(
              //   alignment: Alignment.centerRight,
              //   child: CupertinoButton(
              //     padding: EdgeInsets.all(0),
              //     child: Text("Esqueceu sua senha?"),
              //     onPressed: () => _forgotPassword(context, userService),
              //   ),
              // ),
              // SizedBox(
              //   height: 16,
              // ),
              // Container(
              //   width: double.infinity,
              //   child: AnimatedButton(
              //     onPressed: () => _onLoginSubmit(context),
              //     animatedText: "...",
              //     normalText: "ENTRAR",
              //     filled: true,
              //   ),
              // ),
              // SizedBox(
              //   height: 32,
              // ),
              // Row(
              //   mainAxisAlignment: MainAxisAlignment.center,
              //   children: [
              //     Text("Não tem uma conta?  "),
              //     CupertinoButton(
              //       padding: EdgeInsets.all(0),
              //       child: Text("Criar conta"),
              //       onPressed: () => _onSigUpTap(context),
              //     ),
              //   ],
              // ),
            ],
          ),
        ),
      ),
    );
  }

  void _onLoginSubmit(BuildContext context) async {
    final String username = userController.text;
    final String password = passwordController.text;

    if (username.isEmpty || password.isEmpty) return;

    String message = "";

    try {
      await userService.login(username, password);
      onLoggedOn(context, userService);
      return;
    } on CognitoClientException catch (e) {
      if (e.code == 'InvalidParameterException' ||
          e.code == 'NotAuthorizedException' ||
          e.code == 'UserNotFoundException' ||
          e.code == 'ResourceNotFoundException') {
        message = "Usuário ou senha incorretos";
      } else if (e.code == 'NetworkError') {
        message = "Sem conexão com a internet";
      } else if (e.code == 'UserNotConfirmedException') {
        return await _confirmAccount(context, userService, username, password);
      }
    } catch (e) {
      FLog.error(text: 'CAUGHT EXCEPTION', exception: e);
      message = 'Ops. Aconteceu um erro';
    }
    await dialog.showErrorDialog(context, message);
  }

  void _onSigUpTap(BuildContext context) async {
    await modal.showUnDismissibleModalBottomSheet(
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
              modal.showUnDismissibleModalBottomSheet(
                context,
                TermsAcceptanceWidget(
                  onAccepted: () async {
                    await onSignUpSubmit(context, userService, values);
                  },
                ),
              ),
        ));
  }

  Future<void> onSignUpSubmit(
      BuildContext context, UserService userService, Map values) async {
    try {
      User user = await userService.signUp(values['email'], values['password'],
          attributes: {"given_name": values['name']});
      if (user != null) {
        await _confirmAccount(
            context, userService, values['email'], values['password']);
        Navigator.of(context).pop();
      }
    } on CognitoClientException catch (e) {
      if (e.name == "UsernameExistsException") {
        await dialog.showErrorDialog(context, "E-mail ja cadastrado.");
      }
    }
  }

  Future<void> _confirmAccount(BuildContext context, UserService userService,
      String email, String password) async {
    await modal.showUnDismissibleModalBottomSheet(
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
    await modal.showUnDismissibleModalBottomSheet(
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
              await dialog.showErrorDialog(context,
                  "Você excedeu o número de tentativas, volte mais tarde.");
            } else if (e.name == "CodeMismatchException") {
              await dialog.showErrorDialog(
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
    await modal.showUnDismissibleModalBottomSheet(
      context,
      MultiPrompt(
        promptRequests: [
          SignInEmailConfirmationForPasswordChangePrompt(context),
          SignInPasswordPrompt(),
          SignInPasswordConfirmationPrompt()
        ],
        onSubmit: (values) async {
          await userService.confirmPassword(
              email, values['confirmationCode'], values['password']);
          await dialog.showSuccessDialog(
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
      _onLoginSubmit(context);
    } on CognitoClientException catch (e) {
      if (e.name == "CodeMismatchException") {
        await dialog.showErrorDialog(
            context, "Código de verificação inválido");
      }
      rethrow;
    }
  }

}
