import 'package:goatfolio/services/vandelay/model/import_request.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

Future<Database> initDatabase() async {
  return openDatabase(join(await getDatabasesPath(), 'imports.db'), version: 1,
      onCreate: (db, version) {
    db.execute("CREATE TABLE imports("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "DATETIME INTEGER NOT NULL, "
        "STATUS TEXT"
        ")");
  });
}

Future<void> deleteImportHistoryDatabase() async {
  deleteDatabase(join(await getDatabasesPath(), 'imports.db'));
}

class ImportHistoryStorage {
  static const String TABLE_NAME = "imports";
  final Future<Database> database;

  ImportHistoryStorage() : database = initDatabase();

  Future<void> insert(int datetime, String status) async {
    final Database db = await database;

    await db.insert(
      TABLE_NAME,
      {'datetime': datetime, 'status': status},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  // Future<void> update(StockInvestment investment) async {
  //   final db = await database;
  //
  //   await db.update(
  //     TABLE_NAME,
  //     investment.toJson(),
  //     where: "id = ?",
  //     whereArgs: [investment.id],
  //   );
  // }
  //
  // Future<void> delete(StockInvestment investment) async {
  //   final db = await database;
  //
  //   await db.delete(
  //     TABLE_NAME,
  //     where: "id = ?",
  //     whereArgs: [investment.id],
  //   );
  // }
  //

  Future<ImportStatus> get(String id) async {
    final db = await database;
    final results = await db.query(
      TABLE_NAME,
      where: 'id = ?',
      whereArgs: [id],
    );
    print(results);
    if (results.isNotEmpty) {
      return ImportStatus.fromJson(results[1]);
    }
    return null;
  }

  Future<ImportStatus> getLatest([int limit, int offset]) async {
    final db = await database;

    final List<Map<String, dynamic>> maps = await db.query(TABLE_NAME,
        orderBy: 'ID DESC', limit: limit, offset: offset);

    print(maps);
    return ImportStatus.fromJson(maps[0]);
  }

  Future<void> deleteAll() async {
    final db = await database;
    await db.delete(TABLE_NAME);
  }
}
