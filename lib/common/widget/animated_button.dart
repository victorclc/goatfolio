import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:progress_indicators/progress_indicators.dart';

class AnimatedButton extends StatefulWidget {
  final Function onPressed;
  final String normalText;
  final String animatedText;
  final bool filled;

  const AnimatedButton(
      {Key key,
      @required this.onPressed,
      @required this.normalText,
      @required this.animatedText,
      this.filled = false})
      : super(key: key);

  @override
  _AnimatedButtonState createState() => _AnimatedButtonState();
}

class _AnimatedButtonState extends State<AnimatedButton> {
  bool isLoading = false;

  @override
  Widget build(BuildContext context) {
    return widget.filled ? buildFilled(context) : buildNormal(context);
  }

  Widget buildNormal(BuildContext context) {
    return CupertinoButton(
      child: isLoading
          ? JumpingText(widget.animatedText)
          : Text(widget.normalText),
      onPressed: widget.onPressed != null ? () async {
        if (isLoading) return;
        setState(() {
          isLoading = true;
        });

        await widget.onPressed();

        setState(() {
          isLoading = false;
        });
      }: null,
    );
  }

  Widget buildFilled(BuildContext context) {
    return CupertinoButton.filled(
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
    );
  }
}
