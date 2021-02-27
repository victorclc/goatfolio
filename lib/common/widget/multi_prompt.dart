import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:goatfolio/common/util/focus.dart';
import 'package:goatfolio/common/widget/animated_button.dart';

class MultiPrompt extends StatefulWidget {
  final List<PromptRequest> promptRequests;
  final Function onSubmit;
  final bool keepOpenOnError;

  const MultiPrompt(
      {Key key,
      this.promptRequests,
      this.onSubmit,
      this.keepOpenOnError = true})
      : super(key: key);

  @override
  _MultiPromptState createState() => _MultiPromptState();
}

class _MultiPromptState extends State<MultiPrompt> {
  final PageController pageController = PageController(initialPage: 0);
  PageView pageView;
  int currentPage;
  int lastPage;
  Map<String, String> collectedValues;
  List<PromptPage> pages;

  @override
  void initState() {
    super.initState();
    pages = widget.promptRequests
        .map<PromptPage>((request) => PromptPage(
              request: request,
              onSubmitted: onSubmit,
            ))
        .toList();
    pageView = PageView(
      physics: NeverScrollableScrollPhysics(),
      controller: pageController,
      children: pages,
    );
    lastPage = widget.promptRequests.length - 1;
    currentPage = 0;
    collectedValues = Map();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.95,
      width: double.infinity,
      child: Scaffold(
        resizeToAvoidBottomInset: true,
        resizeToAvoidBottomPadding: true,
        body: SafeArea(
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
                        onTap: previousPage,
                        child: Icon(
                          currentPage == 0 ? Icons.close : Icons.arrow_back,
                          size: 32,
                        ),
                      ),
                    ),
                    Expanded(
                      child: pageView,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void onSubmit(String attrName, String value) async {
    collectedValues[attrName] = value;

    if (currentPage == lastPage) {
      if (widget.onSubmit != null) {
        pages[currentPage].notifySubmitting();
        try {
          await widget.onSubmit(collectedValues);
        } catch (e) {
          if (widget.keepOpenOnError) {
            pages[currentPage].notifySubmittingEnded();
            return;
          }
        }
      }
      Navigator.of(context).pop(collectedValues);
      return;
    }
    nextPage();
  }

  void previousPage() {
    FocusUtils.unfocus(context);
    if (currentPage == 0) {
      Navigator.of(context).pop();
    }
    FocusUtils.unfocus(context);
    currentPage--;
    setState(() {
      pageController.previousPage(
          duration: Duration(milliseconds: 150), curve: Curves.easeIn);
    });
  }

  void nextPage() {
    FocusUtils.unfocus(context);
    ++currentPage;
    setState(() {
      pageController.nextPage(
          duration: Duration(milliseconds: 150), curve: Curves.easeIn);
    });
  }
}

class PromptPage extends StatefulWidget {
  final PromptRequest request;
  final Function onSubmitted;
  static String previousInput;
  _PromptPageState _state;

  void notifySubmitting() {
    _state.notifySubmitting();
  }

  void notifySubmittingEnded() {
    _state.notifySubmittingEnded();
  }

  PromptPage({Key key, this.request, this.onSubmitted}) : super(key: key);

  @override
  _PromptPageState createState() {
    _state = _PromptPageState();
    return _state;
  }
}

class _PromptPageState extends State<PromptPage>
    with AutomaticKeepAliveClientMixin {
  TextEditingController controller = TextEditingController();
  FocusNode focusNode = FocusNode();
  bool validInput;
  bool submitting = false;

  @override
  void initState() {
    super.initState();
    focusNode.requestFocus();
    validInput = widget.request.validate == null;
  }

  void notifySubmitting() {
    setState(() {
      submitting = true;
    });
  }

  void notifySubmittingEnded() {
    setState(() {
      submitting = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Column(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Padding(
            padding:
                const EdgeInsets.only(left: 16.0, right: 16.0, bottom: 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  height: 16,
                ),
                Row(
                  children: [
                    Flexible(child: widget.request.title),
                  ],
                ),
                widget.request.hint ?? Container(),
                Container(
                  width: double.infinity,
                  child: TextField(
                    controller: controller,
                    focusNode: focusNode,
                    obscureText: widget.request.hideText,
                    autofillHints: widget.request.autoFillHints,
                    keyboardType: widget.request.keyboardType,
                    onChanged: validateInput,
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.w500),
                    decoration: new InputDecoration(
                      border: InputBorder.none,
                    ),
                  ),
                ),
                widget.request.footer ?? Container(),
              ],
            ),
          ),
        ),
        Container(
          width: double.infinity,
          padding: EdgeInsets.only(
            top: 8,
            bottom: 8,
          ),
          decoration: BoxDecoration(
            border: Border(
              top: BorderSide(color: Colors.grey),
            ),
          ),
          child: AnimatedButton(
            normalText: "CONTINUAR",
            animatedText: "...",
            onPressed: validInput
                ? () {
                    PromptPage.previousInput = controller.text;
                    widget.onSubmitted(
                        widget.request.attrName, controller.text);
                  }
                : null,
          ),
        ),
      ],
    );
  }

  void validateInput(String input) {
    print(input);
    setState(() {
      if (widget.request.validate != null) {
        validInput = widget.request.validate(input);
      } else {
        validInput = true;
      }
      print(validInput);
    });
  }

  @override
  bool get wantKeepAlive => true;
}

class PromptRequest {
  final Widget title;
  final Widget hint;
  final Widget footer;
  final String attrName;
  final TextInputType keyboardType;
  final List<String> autoFillHints;
  final Function validate;
  final bool hideText;

  PromptRequest({
    this.attrName,
    this.title,
    this.hint,
    this.footer,
    this.keyboardType,
    this.autoFillHints,
    this.validate,
    this.hideText = false,
  });
}
