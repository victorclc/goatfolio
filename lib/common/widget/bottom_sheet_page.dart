import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class BottomSheetPage extends StatelessWidget {
  final Widget child;

  const BottomSheetPage({Key key, this.child}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Column(
                children: [
                  Container(
                    padding: EdgeInsets.only(top: 16, left: 16, right: 16),
                    alignment: Alignment.topLeft,
                    child: GestureDetector(
                      onTap: () => Navigator.of(context).pop(),
                      child: Icon(
                        Icons.close,
                        size: 32,
                      ),
                    ),
                  ),
                  Expanded(
                    child: child,
                  ),
                ],
              ),
            ),
          ],
        ));
  }
}
