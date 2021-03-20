import 'package:flutter/cupertino.dart';

void goToProgressIndicatorScaffold(BuildContext context, String message,
    Function onFinish, Future future) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => ProgressIndicatorScaffold(
        message: message,
        onFinish: onFinish,
        future: future,
      ),
    ),
  );
}

class ProgressIndicatorScaffold extends StatefulWidget {
  final String message;
  final Future future;
  final Function onFinish;

  const ProgressIndicatorScaffold(
      {Key key, this.message, @required this.future, @required this.onFinish})
      : super(key: key);

  @override
  _ProgressIndicatorScaffoldState createState() =>
      _ProgressIndicatorScaffoldState();
}

class _ProgressIndicatorScaffoldState extends State<ProgressIndicatorScaffold> {
  Future<void> onFinish() async {
    await Navigator.of(context).pop();
    await widget.onFinish();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      future: widget.future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          onFinish();
        }
        return CupertinoPageScaffold(
          child: SafeArea(
            child: Center(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CupertinoActivityIndicator(),
                  SizedBox(
                    height: 8,
                  ),
                  Text(
                    widget.message,
                    style: CupertinoTheme.of(context).textTheme.textStyle,
                  )
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
