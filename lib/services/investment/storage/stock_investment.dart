import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

Future<Database> initDatabase() async {
  return openDatabase(
    join(await getDatabasesPath(), 'investments.db'),
    version: 1,
    onCreate: (db, version) {
      db.execute("CREATE TABLE stock_investments("
          "id text not null primary key, "
          "type text, "
          "operation text, "
          "date integer, "
          "broker text, "
          "costs real, "
          "ticker text, "
          "amount integer, "
          "price real"
          ")");
    },
  );
}

Future<void> deleteInvestmentsDatabase() async {
  deleteDatabase(join(await getDatabasesPath(), 'investments.db'));
}

class StockInvestmentStorage {
  static const String TABLE_NAME = "stock_investments";
  final Future<Database> database;

  StockInvestmentStorage() : database = initDatabase();

  Future<void> insert(StockInvestment investment) async {
    final Database db = await database;

    await db.insert(
      TABLE_NAME,
      investment.toJson(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> update(StockInvestment investment) async {
    final db = await database;

    await db.update(
      TABLE_NAME,
      investment.toJson(),
      where: "id = ?",
      whereArgs: [investment.id],
    );
  }

  Future<void> delete(StockInvestment investment) async {
    final db = await database;

    await db.delete(
      TABLE_NAME,
      where: "id = ?",
      whereArgs: [investment.id],
    );
  }

  Future<StockInvestment> get(String id) async {
    final db = await database;
    final results = await db.query(
      TABLE_NAME,
      where: 'id = ?',
      whereArgs: [id],
    );
    if (results.isNotEmpty) {
      return StockInvestment.fromJson(results[1]);
    }
    return null;
  }

  Future<List<StockInvestment>> getAll() async {
    final db = await database;

    final List<Map<String, dynamic>> maps = await db.query(TABLE_NAME);

    return List.generate(maps.length, (i) {
      return StockInvestment.fromJson(maps[i]);
    });
  }

  Future<List<StockInvestment>> getPaginated(int offset, int limit) async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(TABLE_NAME,
        orderBy: 'DATE DESC', limit: limit, offset: offset);

    return List.generate(maps.length, (i) {
      return StockInvestment.fromJson(maps[i]);
    });
  }

  Future<List<String>> getDistinctTickers() async {
    final tickerColumn = "ticker";
    final db = await database;
    final List<Map<String, dynamic>> maps =
        await db.query(TABLE_NAME, distinct: true, columns: [tickerColumn]);

    print("Maps: $maps");
    return List.generate(maps.length, (i) {
      return maps[i][tickerColumn] as String;
    });
  }
}
