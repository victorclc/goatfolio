class CeiImportRequest {
  final String taxId;
  final String password;

  CeiImportRequest({this.taxId, this.password});

  Map<String, dynamic> toJson() => {'tax_id': taxId, 'password': password};
}

class CeiImportResponse {
  final int datetime;
  final String status;

  CeiImportResponse({this.datetime, this.status});

  CeiImportResponse.fromJson(Map<String, dynamic> json)
      : datetime = json['datetime'],
        status = json['status'];

  Map<String, dynamic> toJson() => {'datetime': datetime, 'status': status};
}

class ImportStatus {
  int id;
  int datetime;
  String status;

  ImportStatus({this.id, this.datetime, this.status});

  ImportStatus.fromJson(Map<String, dynamic> json)
      : id = json['ID'],
        datetime = json['DATETIME'],
        status = json['STATUS'];

  Future<Map<String, dynamic>> toJson() async {
    final Map<String, dynamic> json = {};

    if (id != null) {
      json['ID'] = id;
    }
    if (datetime != null) {
      json['DATETIME'] = datetime;
    }
    if (status != null) {
      json['STATUS'] = status;
    }
    return json;
  }

  @override
  String toString() {
    return 'ImportStatus{id: $id, datetime: $datetime, status: $status}';
  }
}
