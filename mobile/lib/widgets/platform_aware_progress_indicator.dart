import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class PlatformAwareProgressIndicator extends StatelessWidget {
  const PlatformAwareProgressIndicator({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Platform.isIOS
        ? Center(child: CupertinoActivityIndicator())
        : Center(
            child: Center(
              child: CircularProgressIndicator(),
            ),
          );
  }
}
