import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:goatfolio/utils/focus.dart' as focusutils;
import 'package:progress_indicators/progress_indicators.dart';

class MultiPrompt extends StatefulWidget {
  final List<PromptRequest> promptRequests;
  final Function onSubmit;
  final bool keepOpenOnError;

  const MultiPrompt(
      {Key? key,
      required this.promptRequests,
      required this.onSubmit,
      this.keepOpenOnError = true})
      : super(key: key);

  @override
  _MultiPromptState createState() => _MultiPromptState();
}

class _MultiPromptState extends State<MultiPrompt> {
  final PageController pageController = PageController(initialPage: 0);
  late PageView pageView;
  late int currentPage;
  late int lastPage;
  late Map<String, String> collectedValues;
  late List<PromptPage> pages;

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
    focusutils.unfocus(context);
    if (currentPage == 0) {
      Navigator.of(context).pop();
    }
    focusutils.unfocus(context);
    currentPage--;
    setState(() {
      pageController.previousPage(
          duration: Duration(milliseconds: 150), curve: Curves.easeIn);
    });
  }

  void nextPage() {
    focusutils.unfocus(context);
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
  static String? previousInput;
  late _PromptPageState _state;

  void notifySubmitting() {
    _state.notifySubmitting();
  }

  void notifySubmittingEnded() {
    _state.notifySubmittingEnded();
  }

  PromptPage({Key? key, required this.request, required this.onSubmitted})
      : super(key: key);

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
  late bool validInput;
  bool submitting = false;
  bool isProcessing = false;

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
                  child: TextFormField(
                    controller: controller,
                    focusNode: focusNode,
                    obscureText: widget.request.hideText,
                    autofillHints: widget.request.autoFillHints,
                    keyboardType: widget.request.keyboardType,
                    validator: widget.request.validateMessages,
                    autovalidateMode: AutovalidateMode.onUserInteraction,
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
          child: CupertinoButton(
            padding: EdgeInsets.all(0),
            child: submitting
                ? JumpingText("...")
                : Text(
                    "CONTINUAR",
                    style: TextStyle(fontSize: 16),
                  ),
            onPressed: validInput
                ? () {
                    if (isProcessing) {
                      return;
                    }
                    isProcessing = true;
                    PromptPage.previousInput = controller.text;
                    widget.onSubmitted(
                        widget.request.attrName, controller.text);
                    isProcessing = false;
                  }
                : null,
          ),
        ),
      ],
    );
  }

  void validateInput(String input) {
    setState(() {
      if (widget.request.validate != null) {
        validInput = widget.request.validate!(input);
      } else {
        validInput = true;
      }
    });
  }

  @override
  bool get wantKeepAlive => true;
}

class PromptRequest {
  final Widget title;
  final Widget? hint;
  final Widget? footer;
  final String attrName;
  final TextInputType? keyboardType;
  final List<String>? autoFillHints;
  final Function? validate;
  final bool hideText;
  final String? Function(String?)? validateMessages;

  PromptRequest({
    required this.attrName,
    required this.title,
    this.hint,
    this.footer,
    this.keyboardType,
    this.autoFillHints,
    this.validate,
    this.hideText = false,
    this.validateMessages,
  });
}
