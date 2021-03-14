class CeiImportRequest {
  final String taxId;
  final String password;

  CeiImportRequest({this.taxId, this.password});

  Map<String, dynamic> toJson() => {'tax_id': taxId, 'password': password};
}
