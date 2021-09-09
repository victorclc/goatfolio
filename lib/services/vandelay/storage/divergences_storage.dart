import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

Future<Database> initDatabase() async {
  return openDatabase(join(await getDatabasesPath(), 'divergences.db'),
      version: 1, onCreate: (db, version) {
    db.execute("CREATE TABLE divergences("
        "TICKER TEXT,"
        'AMOUNT_MISSING INTEGER'
        ")");
  });
}

Future<void> deleteImportHistoryDatabase() async {
  deleteDatabase(join(await getDatabasesPath(), 'divergences.db'));
}

class DivergenceStorage {
  static const String TABLE_NAME = "divergences";
  final Future<Database> database;

  DivergenceStorage() : database = initDatabase();

  Future<void> insert(String ticker, int amountMissing) async {
    final Database db = await database;

    await db.insert(
      TABLE_NAME,
      {'ticker': ticker, 'amount_missing': amountMissing},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Map<String, Object>>> getAll() async {
    final db = await database;
    final results = await db.query(
      TABLE_NAME,
    );
    return results;
  }

  Future<void> delete(String ticker) async {
    final db = await database;
    await db.delete(
      TABLE_NAME,
      where: 'ticker = ?',
      whereArgs: [ticker],
    );
  }

  Future<void> deleteAll() async {
    final db = await database;
    await db.delete(
      TABLE_NAME,
    );
  }
}
