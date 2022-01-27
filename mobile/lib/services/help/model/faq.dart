import 'package:goatfolio/services/help/model/question.dart';

class Faq {
  final String topic;
  final List<Question> questions;

  Faq(this.topic, this.questions);

  Faq.fromJson(Map<String, dynamic> json)
      : topic = json['topic'],
        questions = json['questions']
            .map<Question>((json) => Question.fromJson(json))
            .toList();
}
