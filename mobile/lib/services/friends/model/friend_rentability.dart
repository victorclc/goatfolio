import 'package:goatfolio/services/friends/model/user.dart';
import 'package:goatfolio/services/performance/model/stock_variation.dart';

class Rentability {
  final double dayVariationPerc;
  final double monthVariationPerc;
  final List<StockVariation> tickerVariation;

  Rentability(
    this.dayVariationPerc,
    this.monthVariationPerc,
    this.tickerVariation,
  );

  Rentability.fromJson(Map<String, dynamic> json)
      : dayVariationPerc = json['day_variation_perc'],
        monthVariationPerc = json['month_variation_perc'],
        tickerVariation = json['ticker_variation']
            .map<StockVariation>((json) => StockVariation.fromJson(json))
            .toList();
}

class FriendRentability {
  final FriendUser user;
  final Rentability summary;

  FriendRentability(this.user, this.summary);

  FriendRentability.fromJson(Map<String, dynamic> json)
      : user = FriendUser.fromJson(json['user']),
        summary = Rentability.fromJson(json['summary']);
}
