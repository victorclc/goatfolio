import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/authentication/service/cognito.dart';
import 'package:goatfolio/common/config/app_config.dart';
import 'package:goatfolio/common/constant/app.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/focus.dart';
import 'package:goatfolio/common/widget/animated_button.dart';
import 'package:goatfolio/common/widget/preety_text_field.dart';

class LoginPage extends StatelessWidget {
  final TextEditingController userController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final FocusNode emailNode = FocusNode();
  final FocusNode passwordNode = FocusNode();

  final Function onLoggedOn;

  LoginPage({Key key, @required this.onLoggedOn}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final config = AppConfig.of(context);
    final userService = UserService(config.cognitoUserPoolId,
        config.cognitoClientId, config.cognitoIdentityPoolId);

    return FutureBuilder(
      future: userService.init(),
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          if (snapshot.data) {
            userService.signOut();
            //init returns if the session is valid or not
            return onLoggedOn(userService);
          } else {
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
                            height: 75,
                            width: 75,
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
                            onPressed: () => _forgotPassword(),
                          ),
                        ),
                        SizedBox(
                          height: 16,
                        ),
                        AnimatedButton(
                          onPressed: () => _onLoginSubmit(context, userService),
                          animatedText: "...",
                          normalText: "ENTRAR",
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
                              onPressed: _onSigUpTap,
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
        }
        return Text("Carregando");
      },
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
      return onLoggedOn();
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
        //_goToSignUpConfirmation();
        await _confirmAccount(username, password);
        return _onLoginSubmit(context, userService);
      }
    } catch (e) {
      debugPrint(e.toString());
      message = 'Ops. Aconteceu um erro';
    }
    await DialogUtils.showErrorDialog(context, message);
  }

  void _onSigUpTap() async {
    // await showCupertinoModalBottomSheet(
    //     duration: Duration(milliseconds: 200),
    //     enableDrag: false,
    //     isDismissible: false,
    //     context: context,
    //     builder: (context, controller) {
    //       return GenericPromptList(
    //         keepOpenOnError: true,
    //         promptRequests: [
    //           signInEmailPrompt,
    //           signInPasswordPrompt,
    //           signInPasswordConfirmationPrompt
    //         ],
    //         onSubmit: onSignUpSubmit,
    //       );
    //     });
  }

  Future<void> onSignUpSubmit(Map values) async {
    // try {
    //   User user =
    //       await _userService.signUp(values['email'], values['password']);
    //   if (user != null) {
    //     await _confirmAccount(values['email'], values['password']);
    //   }
    // } on CognitoClientException catch (e) {
    //   if (e.name == "UsernameExistsException") {
    //     await DialogUtils.showErrorDialog(context, "E-mail ja cadastrado.");
    //   } else {
    //     print(e);
    //   }
    // }
  }

  Future<void> _confirmAccount(String email, String password) async {
    // await showCupertinoModalBottomSheet(
    //     duration: Duration(milliseconds: 200),
    //     enableDrag: false,
    //     isDismissible: false,
    //     context: context,
    //     builder: (context, controller) {
    //       return GenericPromptList(
    //         promptRequests: [
    //           _buildEmailConfirmationPrompt(),
    //         ],
    //         onSubmit: (values) =>
    //             onConfirmAccountSubmit(email, password, values),
    //       );
    //     });
  }

  Future<void> _forgotPassword() async {
    // await showCupertinoModalBottomSheet(
    //     duration: Duration(milliseconds: 200),
    //     enableDrag: false,
    //     isDismissible: false,
    //     context: context,
    //     builder: (context, controller) {
    //       return GenericPromptList(
    //         promptRequests: [
    //           forgotPasswordPrompt,
    //         ],
    //         onSubmit: (values) async {
    //           try {
    //             await _userService.forgotPassword(values['email']);
    //             await _confirmPassword(values['email']);
    //           } on CognitoClientException catch (e) {
    //             if (e.name == "LimitExceededException") {
    //               await DialogUtils.showErrorDialog(context,
    //                   "Você excedeu o número de tentativas, volte mais tarde.");
    //             } else if (e.name == "CodeMismatchException") {
    //               await DialogUtils.showErrorDialog(
    //                   context, "Código de verificação inválido");
    //             }
    //             rethrow;
    //           }
    //         },
    //       );
    //     });
  }

  Future<void> _confirmPassword(String email) async {
    // await showCupertinoModalBottomSheet(
    //     duration: Duration(milliseconds: 200),
    //     enableDrag: false,
    //     isDismissible: false,
    //     context: context,
    //     builder: (context, controller) {
    //       return GenericPromptList(
    //         promptRequests: [
    //           _buildEmailConfirmationForPasswordChangePrompt(),
    //           signInPasswordPrompt,
    //           signInPasswordConfirmationPrompt,
    //         ],
    //         onSubmit: (values) async {
    //           await _userService.confirmPassword(
    //               email, values['confirmationCode'], values['password']);
    //           DialogUtils.showSuccessDialog(
    //               context, "Sua senha foi alterada com sucesso!");
    //         },
    //       );
    //     });
  }

  Future<void> onConfirmAccountSubmit(
      String email, String password, Map values) async {
    // try {
    //   await _userService.confirmAccount(email, values['confirmationCode']);
    //   userController.text = email;
    //   passwordController.text = password;
    //   _onLoginSubmit();
    // } on CognitoClientException catch (e) {
    //   if (e.name == "CodeMismatchException") {
    //     await DialogUtils.showErrorDialog(
    //         context, "Código de verificação inválido");
    //   }
    //   rethrow;
    // }
  }

//   final PromptRequest signInEmailPrompt = PromptRequest(
//     attrName: 'email',
//     title: Row(
//       children: [
//         Text(
//           "Qual seu ",
//           style: TextStyle(fontSize: 24),
//         ),
//         Text(
//           "e-mail",
//           style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
//         ),
//         Text(
//           "?",
//           style: TextStyle(fontSize: 24),
//         ),
//       ],
//     ),
//     hint: Text(
//       "Será usado como sua identificação pelo Goatfolio.",
//       style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
//     ),
//     keyboardType: TextInputType.emailAddress,
//     autoFillHints: [AutofillHints.email],
//     validate: (input) => RegExp(
//             r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?)*$")
//         .hasMatch(input),
//   );
//
//   final PromptRequest signInPasswordPrompt = PromptRequest(
//     attrName: 'password',
//     title: Row(
//       children: [
//         Text(
//           "Crie uma ",
//           style: TextStyle(fontSize: 24),
//         ),
//         Text(
//           "senha",
//           style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
//         ),
//       ],
//     ),
//     hint: Text(
//       "No mínimo 8 caracteres, use números, letras maiúsculas e minúsculas na composição da sua senha.",
//       style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
//     ),
//     keyboardType: TextInputType.visiblePassword,
//     autoFillHints: [AutofillHints.password],
//     hideText: true,
//     validate: (String input) =>
//         RegExp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$")
//             .hasMatch(input),
//   );
//
//   final PromptRequest signInPasswordConfirmationPrompt = PromptRequest(
//     attrName: 'password',
//     title: Row(
//       children: [
//         Text(
//           "Confirme a ",
//           style: TextStyle(fontSize: 24),
//         ),
//         Text(
//           "senha",
//           style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
//         ),
//       ],
//     ),
//     hint: Container(),
//     keyboardType: TextInputType.visiblePassword,
//     autoFillHints: [AutofillHints.password],
//     hideText: true,
//     validate: (input) => input == PromptPage.previousInput,
//   );
//
//   final PromptRequest forgotPasswordPrompt = PromptRequest(
//     attrName: 'email',
//     title: Row(
//       children: [
//         Text(
//           "Qual seu ",
//           style: TextStyle(fontSize: 24),
//         ),
//         Text(
//           "e-mail",
//           style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
//         ),
//         Text(
//           "?",
//           style: TextStyle(fontSize: 24),
//         ),
//       ],
//     ),
//     keyboardType: TextInputType.emailAddress,
//     autoFillHints: [AutofillHints.email],
//     validate: (input) => RegExp(
//             r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?)*$")
//         .hasMatch(input),
//   );
//
//   PromptRequest _buildEmailConfirmationPrompt() {
//     return PromptRequest(
//       attrName: 'confirmationCode',
//       title: RichText(
//         text: TextSpan(
//           text: 'Digite o ',
//           style: GoatfolioStyles.defaultStyle.copyWith(fontSize: 24),
//           children: <TextSpan>[
//             TextSpan(
//                 text: 'código', style: TextStyle(fontWeight: FontWeight.bold)),
//             TextSpan(text: ' que enviamos no seu email'),
//           ],
//         ),
//       ),
//       hint: Text(
//         "Precisamos verificar seu e-mail, é a unica forma de recuperar sua conta caso esqueça sua senha",
//         style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
//       ),
//       footer: CupertinoButton(
//         padding: EdgeInsets.only(top: 16),
//         child: Text("Reenviar código"),
//         onPressed: () =>
//             _userService.resendConfirmationCode(userController.text),
//       ),
//       keyboardType: TextInputType.number,
//     );
//   }
//
//   PromptRequest _buildEmailConfirmationForPasswordChangePrompt() {
//     return PromptRequest(
//       attrName: 'confirmationCode',
//       title: RichText(
//         text: TextSpan(
//           text: 'Digite o ',
//           style: GoatfolioStyles.defaultStyle.copyWith(fontSize: 24),
//           children: <TextSpan>[
//             TextSpan(
//                 text: 'código', style: TextStyle(fontWeight: FontWeight.bold)),
//             TextSpan(text: ' que enviamos no seu email'),
//           ],
//         ),
//       ),
//       hint: Text(
//         "Precisamos verificar se você é realmente você.",
//         style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
//       ),
//       keyboardType: TextInputType.number,
//     );
//   }
}
