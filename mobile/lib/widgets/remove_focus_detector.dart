import 'package:flutter/cupertino.dart';

class RemoveFocusDetector extends StatelessWidget {
  final Widget child;

  const RemoveFocusDetector({Key? key, required this.child}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        FocusScopeNode currentFocus = FocusScope.of(context);
        if (!currentFocus.hasPrimaryFocus) {
          currentFocus.unfocus();
        }
      },
      child: this.child,
    );
  }
}
