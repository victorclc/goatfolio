import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/pages/add/screen/stock_list.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

import 'cei_login.dart';

class AddPage extends StatelessWidget {
  static const icon = Icon(Icons.add);
  static const String title = "Adicionar";
  static const Color backgroundGray = Color(0xFFEFEFF4);

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(),
      child: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SettingsList(
                shrinkWrap: true,
                lightBackgroundColor:
                    MediaQuery.of(context).platformBrightness !=
                            Brightness.light
                        ? CupertinoTheme.of(context).scaffoldBackgroundColor
                        : null,
                physics: NeverScrollableScrollPhysics(),
                sections: [
                  SettingsSection(
                    title: "RENDA VARIÁVEL",
                    // subtitle: Text("RENDA VARIAVEL"),
                    // titlePadding: EdgeInsets.all(0),
                    // subtitlePadding: EdgeInsets.all(0),
                    tiles: [
                      SettingsTile(
                        title: 'Importar automaticamente (CEI)',
                        onPressed: (context) =>
                            ModalUtils.showDragableModalBottomSheet(
                          context,
                          CeiLoginPage(
                              userService: Provider.of<UserService>(context,
                                  listen: false)),
                        ),
                      ),
                      SettingsTile(
                        title: 'Operação de compra',
                        onPressed: (context) =>
                            goToInvestmentList(context, true),
                      ),
                      SettingsTile(
                        title: 'Operação de venda',
                        onPressed: (context) =>
                            goToInvestmentList(context, false),
                      ),
                    ],
                  ),
                  SettingsSection(
                    tiles: [],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class BetterSettingsTile extends SettingsTile {
  Widget iosTile(BuildContext context) {
    // if (_tileType == _SettingsTileType.switchTile) {
    //   return CupertinoSettingsItem(
    //     enabled: enabled,
    //     type: SettingsItemType.toggle,
    //     label: title,
    //     labelMaxLines: titleMaxLines,
    //     leading: leading,
    //     subtitle: subtitle,
    //     subtitleMaxLines: subtitleMaxLines,
    //     switchValue: switchValue,
    //     onToggle: onToggle,
    //     labelTextStyle: titleTextStyle,
    //     switchActiveColor: switchActiveColor,
    //     subtitleTextStyle: subtitleTextStyle,
    //     valueTextStyle: subtitleTextStyle,
    //     trailing: trailing,
    //   );
    // } else {
    return BetterCupertinoSettingsItem(
      enabled: enabled,
      type: SettingsItemType.modal,
      label: title,
      labelMaxLines: titleMaxLines,
      value: subtitle,
      trailing: trailing,
      iosChevron: iosChevron,
      iosChevronPadding: iosChevronPadding,
      hasDetails: false,
      leading: leading,
      onPress: onTapFunction(context),
      labelTextStyle: titleTextStyle,
      subtitleTextStyle: subtitleTextStyle,
      valueTextStyle: subtitleTextStyle,
    );
  }
}

enum SettingsItemType {
  toggle,
  modal,
}

typedef void PressOperationCallback();

class BetterCupertinoSettingsItem extends StatefulWidget {
  const BetterCupertinoSettingsItem({
    @required this.type,
    @required this.label,
    this.labelMaxLines,
    this.subtitle,
    this.subtitleMaxLines,
    this.leading,
    this.trailing,
    this.iosChevron = defaultCupertinoForwardIcon,
    this.iosChevronPadding = defaultCupertinoForwardPadding,
    this.value,
    this.hasDetails = false,
    this.enabled = true,
    this.onPress,
    this.switchValue = false,
    this.onToggle,
    this.labelTextStyle,
    this.subtitleTextStyle,
    this.valueTextStyle,
    this.switchActiveColor,
  })  : assert(label != null),
        assert(type != null),
        assert(labelMaxLines == null || labelMaxLines > 0),
        assert(subtitleMaxLines == null || subtitleMaxLines > 0);

  final String label;
  final int labelMaxLines;
  final String subtitle;
  final int subtitleMaxLines;
  final Widget leading;
  final Widget trailing;
  final Icon iosChevron;
  final EdgeInsetsGeometry iosChevronPadding;
  final SettingsItemType type;
  final String value;
  final bool hasDetails;
  final bool enabled;
  final PressOperationCallback onPress;
  final bool switchValue;
  final Function(bool value) onToggle;
  final TextStyle labelTextStyle;
  final TextStyle subtitleTextStyle;
  final TextStyle valueTextStyle;
  final Color switchActiveColor;

  @override
  State<StatefulWidget> createState() => new BetterCupertinoSettingsItemState();
}

class BetterCupertinoSettingsItemState
    extends State<BetterCupertinoSettingsItem> {
  bool pressed = false;
  bool _checked;

  @override
  Widget build(BuildContext context) {
    _checked = widget.switchValue;

    final ThemeData theme = Theme.of(context);
    final ListTileTheme tileTheme = ListTileTheme.of(context);
    IconThemeData iconThemeData;
    if (widget.leading != null)
      iconThemeData = IconThemeData(
        color: widget.enabled
            ? _iconColor(theme, tileTheme)
            : CupertinoColors.inactiveGray,
      );

    Widget leadingIcon;
    if (widget.leading != null) {
      leadingIcon = IconTheme.merge(
        data: iconThemeData,
        child: widget.leading,
      );
    }

    List<Widget> rowChildren = [];
    if (leadingIcon != null) {
      rowChildren.add(
        Padding(
          padding: const EdgeInsetsDirectional.only(
            start: 15.0,
          ),
          child: leadingIcon,
        ),
      );
    }

    Widget titleSection;
    if (widget.subtitle == null) {
      titleSection = Padding(
        padding: EdgeInsets.only(top: 1.5),
        child: Text(
          widget.label,
          overflow: TextOverflow.ellipsis,
          style: widget.labelTextStyle ??
              TextStyle(
                fontSize: 16,
                color: widget.enabled ? null : CupertinoColors.inactiveGray,
              ),
        ),
      );
    } else {
      titleSection = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          const Padding(padding: EdgeInsets.only(top: 8.5)),
          Text(
            widget.label,
            overflow: TextOverflow.ellipsis,
            style: widget.labelTextStyle,
          ),
          const Padding(padding: EdgeInsets.only(top: 4.0)),
          Text(
            widget.subtitle,
            maxLines: widget.subtitleMaxLines,
            overflow: TextOverflow.ellipsis,
            style: widget.subtitleTextStyle ??
                TextStyle(
                  fontSize: 12.0,
                  letterSpacing: -0.2,
                ),
          )
        ],
      );
    }

    rowChildren.add(
      Expanded(
        child: Padding(
          padding: const EdgeInsetsDirectional.only(
            start: 15.0,
            end: 15.0,
          ),
          child: titleSection,
        ),
      ),
    );

    switch (widget.type) {
      case SettingsItemType.toggle:
        rowChildren.add(
          Padding(
            padding: const EdgeInsetsDirectional.only(end: 11.0),
            child: CupertinoSwitch(
              value: widget.switchValue,
              activeColor: widget.enabled
                  ? (widget.switchActiveColor ?? Theme.of(context).accentColor)
                  : CupertinoColors.inactiveGray,
              onChanged: !widget.enabled
                  ? null
                  : (bool value) {
                      widget.onToggle(value);
                    },
            ),
          ),
        );
        break;
      case SettingsItemType.modal:
        final List<Widget> rightRowChildren = [];
        if (widget.value != null) {
          rightRowChildren.add(
            Padding(
              padding: const EdgeInsetsDirectional.only(
                top: 1.5,
                end: 2.25,
              ),
              child: Text(
                widget.value,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.end,
                style: widget.valueTextStyle ??
                    TextStyle(
                      color: CupertinoColors.inactiveGray,
                      fontSize: 16,
                    ),
              ),
            ),
          );
        }

        if (widget.trailing != null) {
          rightRowChildren.add(
            Padding(
              padding: const EdgeInsetsDirectional.only(
                top: 0.5,
                start: 2.25,
              ),
              child: widget.trailing,
            ),
          );
        }

        if (widget.iosChevron != null) {
          rightRowChildren.add(
            widget.iosChevronPadding == null
                ? widget.iosChevron
                : Padding(
                    padding: widget.iosChevronPadding,
                    child: widget.iosChevron,
                  ),
          );
        }

        rightRowChildren.add(const SizedBox(width: 8.5));

        rowChildren.add(
          Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.end,
            children: rightRowChildren,
          ),
        );

        break;
    }

    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: () {
        if ((widget.onPress != null || widget.onToggle != null) &&
            widget.enabled) {
          if (mounted) {
            setState(() {
              pressed = true;
            });
          }

          if (widget.onPress != null) {
            widget.onPress();
          }

          Future.delayed(const Duration(milliseconds: 100), () {
            if (mounted) {
              setState(() {
                pressed = false;
              });
            }
          });
        }

        if (widget.type == SettingsItemType.toggle && widget.enabled) {
          if (mounted) {
            setState(() {
              _checked = !_checked;
              widget.onToggle(_checked);
            });
          }
        }
      },
      onTapUp: (_) {
        if (widget.enabled && mounted) {
          setState(() {
            pressed = false;
          });
        }
      },
      onTapDown: (_) {
        if (widget.enabled && mounted) {
          setState(() {
            pressed = true;
          });
        }
      },
      onTapCancel: () {
        if (widget.enabled && mounted) {
          setState(() {
            pressed = false;
          });
        }
      },
      child: Container(
        color: calculateBackgroundColor(context),
        height: widget.subtitle == null ? 44.0 : 57.0,
        child: Row(
          children: rowChildren,
        ),
      ),
    );
  }

  Color calculateBackgroundColor(BuildContext context) =>
      MediaQuery.of(context).platformBrightness == Brightness.light
          ? pressed
              ? iosPressedTileColorLight
              : Colors.white
          : pressed
              ? iosPressedTileColorDark
              : iosTileDarkColor;

  Color _iconColor(ThemeData theme, ListTileTheme tileTheme) {
    if (tileTheme?.selectedColor != null) {
      return tileTheme.selectedColor;
    }

    if (tileTheme?.iconColor != null) {
      return tileTheme.iconColor;
    }

    switch (theme.brightness) {
      case Brightness.light:
        return Colors.black45;
      case Brightness.dark:
        return null; // null - use current icon theme color
    }
    assert(theme.brightness != null);
    return null;
  }
}

const Color mediumGrayColor = Color(0xFFC7C7CC);
const Color itemPressedColor = Color(0xFFD9D9D9);
const Color borderColor = Color(0xFFBCBBC1);
const Color borderLightColor = Color.fromRGBO(49, 44, 51, 1);
const Color backgroundGray = Color(0xFFEFEFF4);
const Color groupSubtitle = Color(0xFF777777);
const Color iosTileDarkColor = Color.fromRGBO(28, 28, 30, 1);
const Color iosPressedTileColorDark = Color.fromRGBO(44, 44, 46, 1);
const Color iosPressedTileColorLight = Color.fromRGBO(230, 229, 235, 1);

const defaultTitlePadding = EdgeInsets.only(
  left: 15.0,
  right: 15.0,
  bottom: 6.0,
);

const defaultCupertinoForwardIcon = Icon(
  CupertinoIcons.forward,
  size: 21.0,
  color: mediumGrayColor,
);

const defaultCupertinoForwardPadding = EdgeInsetsDirectional.only(
  start: 2.25,
);
