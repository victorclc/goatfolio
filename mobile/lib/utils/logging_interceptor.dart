import 'package:f_logs/f_logs.dart';
import 'package:flutter/cupertino.dart';
import 'package:http_interceptor/http_interceptor.dart';

import 'package:http_interceptor/models/request_data.dart';
import 'package:http_interceptor/models/response_data.dart';

class LoggingInterceptor implements InterceptorContract {
  @override
  Future<RequestData> interceptRequest({required RequestData data}) async {
    FLog.debug(text: 'url: ${data.url}');
    FLog.debug(text: 'headers: ${data.headers}');
    FLog.debug(text: 'Request');
    FLog.debug(text: 'body: ${data.body}');
    return data;
  }

  @override
  Future<ResponseData> interceptResponse({required ResponseData data}) async {
    FLog.debug(text: 'Response');
    FLog.debug(text: 'status code: ${data.statusCode}');
    FLog.debug(text: 'headers: ${data.headers}');
    FLog.debug(text: 'body: ${data.body}');
    return data;
  }
}