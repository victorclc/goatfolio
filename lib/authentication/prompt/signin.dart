import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';

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
            validate: (input) => RegExp(
                    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?)*$")
                .hasMatch(input));
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
              RegExp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$") //TODO ATUALIZAR REGEX E HINT
                  .hasMatch(input),
        );
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
        );
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
          validate: (input) => RegExp(
                  r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,253}[a-zA-Z0-9])?)*$")
              .hasMatch(input),
        );
}

class SignInEmailConfirmationPrompt extends PromptRequest {
  SignInEmailConfirmationPrompt(
    Function onResendPressed,
  ) : super(
          attrName: 'confirmationCode',
          title: Row(
            children: [
              Text(
                "Digite o ",
                style: TextStyle(fontSize: 24),
              ),
              Text(
                "código",
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              Text(
                "que enviamos no seu email",
                style: TextStyle(fontSize: 24),
              ),
            ],
          ),
          hint: Text(
            "Precisamos verificar seu e-mail, é a unica forma de recuperar sua conta caso esqueça sua senha",
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
          ),
          footer: CupertinoButton(
            padding: EdgeInsets.only(top: 16),
            child: Text("Reenviar código"),
            onPressed: onResendPressed(),
          ),
          keyboardType: TextInputType.number,
        );
}

class SignInEmailConfirmationForPasswordChangePrompt extends PromptRequest {
  SignInEmailConfirmationForPasswordChangePrompt()
      : super(
          attrName: 'confirmationCode',
          title: Row(
            children: [
              Text(
                "Digite o ",
                style: TextStyle(fontSize: 24),
              ),
              Text(
                "código",
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              Text(
                "que enviamos no seu email",
                style: TextStyle(fontSize: 24),
              ),
            ],
          ),
          hint: Text(
            "Precisamos verificar se você é realmente você.",
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
          ),
          keyboardType: TextInputType.number,
        );
}
