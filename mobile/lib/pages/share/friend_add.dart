import 'package:flutter/cupertino.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/client/client.dart';
import 'package:goatfolio/services/friends/cubit/friends_list_cubit.dart';
import 'package:goatfolio/utils/dialog.dart' as dialog;
import 'package:goatfolio/utils/modal.dart' as modal;
import 'package:goatfolio/widgets/progress_indicator_scaffold.dart';

const BorderSide _kDefaultRoundedBorderSide = BorderSide(
  color: CupertinoDynamicColor.withBrightness(
    color: Color(0x33000000),
    darkColor: Color(0x33FFFFFF),
  ),
  style: BorderStyle.solid,
  width: 0.0,
);

const Border _kDefaultRoundedBorder = Border(
  bottom: _kDefaultRoundedBorderSide,
);

const BoxDecoration _kDefaultRoundedBorderDecoration = BoxDecoration(
  color: CupertinoDynamicColor.withBrightness(
    color: CupertinoColors.white,
    darkColor: CupertinoColors.black,
  ),
  border: _kDefaultRoundedBorder,
  // borderRadius: BorderRadius.all(Radius.circular(5.0)),
);

class FriendAdd extends StatefulWidget {
  final UserService userService;

  const FriendAdd({Key? key, required this.userService}) : super(key: key);

  @override
  _FriendAddState createState() => _FriendAddState();
}

class _FriendAddState extends State<FriendAdd> {
  final TextEditingController _emailController = TextEditingController();
  late FriendsClient service;
  late Future<String> _future;

  @override
  void initState() {
    super.initState();
    service = FriendsClient(widget.userService);
    _emailController.text = '';
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          border: null,
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          leading: CupertinoButton(
            padding: EdgeInsets.all(0),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              widthFactor: 1.0,
              child: Text(
                'Cancelar',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            onPressed: () => Navigator.of(context).pop(),
          ),
          middle: Text(
            "Compartilhar",
            style: textTheme.navTitleTextStyle,
          ),
          trailing: CupertinoButton(
            padding: EdgeInsets.all(0),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              widthFactor: 1.0,
              child: Text(
                'Enviar',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            onPressed: canSubmit() ? onSubmit : null,
          ),
        ),
        child: SingleChildScrollView(
          child: Column(
            children: [
              SizedBox(
                height: 32,
              ),
              CupertinoTextField(
                controller: _emailController,
                autofocus: true,
                onChanged: (something) {
                  setState(() {});
                },
                decoration: _kDefaultRoundedBorderDecoration,
                textInputAction: TextInputAction.next,
                inputFormatters: [],
                keyboardType: TextInputType.emailAddress,
                prefix: Container(
                  width: 80,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Para',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "E-mail",
                enableSuggestions: false,
                autocorrect: false,
              ),
            ],
          ),
        ));
  }

  List<String> validateForm() {
    return [];
  }

  void onSubmit() async {
    try {
      final problems = validateForm();
      if (problems.isNotEmpty) {
        final List<Widget> problemWidgets = [];
        problems.forEach((description) {
          problemWidgets.add(Text(description));
        });
        await dialog.showCustomErrorDialog(
            context,
            Column(
              children: problemWidgets,
            ));
        return;
      }
    } on Exception catch (e) {
      await dialog.showErrorDialog(context, "Dados invalidos.");
      return;
    }

    _future = BlocProvider.of<FriendsListCubit>(context)
        .add(_emailController.text);

    modal.showUnDismissibleModalBottomSheet(
      context,
      ProgressIndicatorScaffold(
          message: 'Enviando convite...',
          future: _future,
          onFinish: () async {
            try {
              final message = await _future;
              await dialog.showSuccessDialog(context, message);
              BlocProvider.of<FriendsListCubit>(context).refresh();
              Navigator.of(context).pop();
            } on Exception catch (e) {
              await dialog.showErrorDialog(
                  context, e.toString().replaceAll("Exception: ", ""));
            }
          }),
    );
  }

  bool canSubmit() {
    return _emailController.text.isNotEmpty;
  }
}
