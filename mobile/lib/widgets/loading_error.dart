import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class LoadingError extends StatelessWidget {
  final Function() onRefreshPressed;

  const LoadingError({Key? key, required this.onRefreshPressed})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        SizedBox(
          height: 32,
        ),
        Text("Tivemos um problema ao carregar", style: textTheme.textStyle),
        Text(" as informações.", style: textTheme.textStyle),
        SizedBox(
          height: 8,
        ),
        Text("Toque para tentar novamente.", style: textTheme.textStyle),
        CupertinoButton(
          padding: EdgeInsets.all(0),
          child: Icon(
            Icons.refresh_outlined,
            size: 32,
          ),
          onPressed: onRefreshPressed,
        ),
      ],
    );
  }
}
