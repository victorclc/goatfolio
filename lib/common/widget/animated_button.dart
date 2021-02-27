import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:progress_indicators/progress_indicators.dart';

class AnimatedButton extends StatefulWidget {
  final Function onPressed;
  final String normalText;
  final String animatedText;

  const AnimatedButton(
      {Key key, @required this.onPressed, this.normalText, this.animatedText})
      : super(key: key);

  @override
  _AnimatedButtonState createState() => _AnimatedButtonState();
}

class _AnimatedButtonState extends State<AnimatedButton> {
  bool isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      child: CupertinoButton.filled(
        child: isLoading
            ? JumpingText(widget.animatedText)
            : Text(widget.normalText),
        onPressed: () async {
          if (isLoading) return;
          setState(() {
            isLoading = true;
          });
          await widget.onPressed();
          setState(() {
            isLoading = false;
          });
        },
      ),
    );
  }
}
