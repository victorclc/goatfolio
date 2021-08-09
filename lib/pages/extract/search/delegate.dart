import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/search/cupertino_search_delegate.dart';
import 'package:goatfolio/services/investment/model/stock.dart';

class ExtractSearchDelegate extends SearchCupertinoDelegate {
  final Function searchFunction;
  final Function buildFunction;
  List<StockInvestment> results = [];
  ScrollController controller = ScrollController();
  String lastQuery = "";
  Future _future;

  ExtractSearchDelegate(this.searchFunction, this.buildFunction) {
    controller.addListener(() {
      focusNode.unfocus();
    });
  }

  @override
  List<Widget> buildActions(BuildContext context) {
    return [];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return Container();
  }

  @override
  Widget buildResults(BuildContext context) {
    if (query.isEmpty) {
      return Container();
    }
    if (lastQuery != query) {
      _future = searchFunction(query);
    }
    lastQuery = query;
    return FutureBuilder(
      future: _future,
      builder: (context, snapshot) {
        switch (snapshot.connectionState) {
          case ConnectionState.none:
          case ConnectionState.active:
            break;
          case ConnectionState.waiting:
            return Center(
                child: Platform.isIOS
                    ? CupertinoActivityIndicator()
                    : CircularProgressIndicator());
          case ConnectionState.done:
            if (snapshot.hasData) {
              return SingleChildScrollView(
                  controller: controller,
                  child: Padding(
                    padding: EdgeInsets.only(top: 16),
                    child: buildFunction(context, snapshot.data),
                  ));
            }
        }
        return Container();
      },
    );
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    return Container();
  }
}

class ExtractAndroidSearchDelegate extends SearchDelegate {
  final Function searchFunction;
  final Function buildFunction;
  List<StockInvestment> results = [];
  ScrollController controller = ScrollController();
  String lastQuery = "";
  Future _future;

  ExtractAndroidSearchDelegate(this.searchFunction, this.buildFunction);

  @override
  List<Widget> buildActions(BuildContext context) {
    return [];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return BackButton();
  }

  @override
  Widget buildResults(BuildContext context) {
    if (query.isEmpty) {
      return Container();
    }
    if (lastQuery != query) {
      _future = searchFunction(query);
    }
    lastQuery = query;
    return FutureBuilder(
      future: _future,
      builder: (context, snapshot) {
        switch (snapshot.connectionState) {
          case ConnectionState.none:
          case ConnectionState.active:
            break;
          case ConnectionState.waiting:
            return Center(child: CircularProgressIndicator());
          case ConnectionState.done:
            if (snapshot.hasData) {
              return SingleChildScrollView(
                  controller: controller,
                  child: Padding(
                    padding: EdgeInsets.only(top: 16),
                    child: buildFunction(context, snapshot.data),
                  ));
            }
        }
        return Container();
      },
    );
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    return Container();
  }
}
