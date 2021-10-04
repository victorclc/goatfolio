import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/authentication/cognito.dart';
import 'package:goatfolio/widgets/multi_prompt.dart';

const String VALID_EMAIL =
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?)*$";
const String PASSWORD_STRENGTH =
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$";

class SignInEmailPrompt extends PromptRequest {
  SignInEmailPrompt()
      : super(
            attrName: 'email',
            title: Row(
              children: [
                Text(
                  "Qual seu ",
                  style: TextStyle(fontSize: 24),
                ),
                Text(
                  "e-mail",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                Text(
                  "?",
                  style: TextStyle(fontSize: 24),
                ),
              ],
            ),
            hint: Text(
              "Será usado como sua identificação pelo Goatfolio.",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
            ),
            keyboardType: TextInputType.emailAddress,
            autoFillHints: [AutofillHints.email],
            validate: (input) => RegExp(VALID_EMAIL).hasMatch(input));
}

class SignInNamePrompt extends PromptRequest {
  SignInNamePrompt()
      : super(
            attrName: 'name',
            title: Row(
              children: [
                Text(
                  "Qual seu ",
                  style: TextStyle(fontSize: 24),
                ),
                Text(
                  "nome",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                Text(
                  " ou ",
                  style: TextStyle(fontSize: 24),
                ),
                Text(
                  "apelido",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                Text(
                  "?",
                  style: TextStyle(fontSize: 24),
                ),
              ],
            ),
            hint: Text(
              "Como gostaria de ser chamado?",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
            ),
            keyboardType: TextInputType.text,
            autoFillHints: [AutofillHints.givenName]);
}

class SignInPasswordPrompt extends PromptRequest {
  SignInPasswordPrompt()
      : super(
            attrName: 'password',
            title: Row(
              children: [
                Text(
                  "Crie uma ",
                  style: TextStyle(fontSize: 24),
                ),
                Text(
                  "senha",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            hint: Text(
              "No mínimo 8 caracteres, use números, letras maiúsculas e minúsculas na composição da sua senha.",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
            ),
            keyboardType: TextInputType.visiblePassword,
            autoFillHints: [AutofillHints.password],
            hideText: true,
            validate: (String input) =>
                RegExp(PASSWORD_STRENGTH).hasMatch(input),
            validateMessages: (String? input) {
              if (input == null || !RegExp(PASSWORD_STRENGTH).hasMatch(input)) {
                return "Senha não atende requisitos mínimos";
              }
            });
}

class SignInPasswordConfirmationPrompt extends PromptRequest {
  SignInPasswordConfirmationPrompt()
      : super(
            attrName: 'password',
            title: Row(
              children: [
                Text(
                  "Confirme a ",
                  style: TextStyle(fontSize: 24),
                ),
                Text(
                  "senha",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            hint: Container(),
            keyboardType: TextInputType.visiblePassword,
            autoFillHints: [AutofillHints.password],
            hideText: true,
            validate: (input) => input == PromptPage.previousInput,
            validateMessages: (String? input) {
              if (input != PromptPage.previousInput) {
                return "Senhas não batem";
              }
            });
}

class SignInForgotPasswordPrompt extends PromptRequest {
  SignInForgotPasswordPrompt()
      : super(
          attrName: 'email',
          title: Row(
            children: [
              Text(
                "Qual seu ",
                style: TextStyle(fontSize: 24),
              ),
              Text(
                "e-mail",
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              Text(
                "?",
                style: TextStyle(fontSize: 24),
              ),
            ],
          ),
          keyboardType: TextInputType.emailAddress,
          autoFillHints: [AutofillHints.email],
          validate: (String input) => RegExp(VALID_EMAIL).hasMatch(input),
        );
}

class SignInEmailConfirmationPrompt extends PromptRequest {
  SignInEmailConfirmationPrompt(
    BuildContext context,
    UserService userService,
    String email,
  ) : super(
          attrName: 'confirmationCode',
          title: RichText(
            text: TextSpan(
              text: 'Digite o ',
              style:
                  Theme.of(context).textTheme.bodyText2!.copyWith(fontSize: 24),
              children: <TextSpan>[
                TextSpan(
                    text: 'código',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                TextSpan(text: ' que enviamos no seu email'),
              ],
            ),
          ),
          hint: Text(
            "Precisamos verificar seu e-mail, é a unica forma de recuperar sua conta caso esqueça sua senha",
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
          ),
          footer: CupertinoButton(
            padding: EdgeInsets.only(top: 16),
            child: Text("Reenviar código"),
            onPressed: () {
              userService.resendConfirmationCode(email);
            },
          ),
          keyboardType: TextInputType.number,
        );
}

class SignInEmailConfirmationForPasswordChangePrompt extends PromptRequest {
  SignInEmailConfirmationForPasswordChangePrompt(BuildContext context)
      : super(
          attrName: 'confirmationCode',
          title: RichText(
            text: TextSpan(
              text: 'Digite o ',
              style:
                  Theme.of(context).textTheme.bodyText2!.copyWith(fontSize: 24),
              children: <TextSpan>[
                TextSpan(
                    text: 'código',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                TextSpan(text: ' que enviamos no seu email'),
              ],
            ),
          ),
          hint: Text(
            "Precisamos verificar se você é realmente você.",
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
          ),
          keyboardType: TextInputType.number,
        );
}
