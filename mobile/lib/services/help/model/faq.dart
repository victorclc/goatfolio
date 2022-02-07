import 'package:goatfolio/services/help/model/question.dart';

class Faq {
  final String topic;
  final String description;
  final List<Question> questions;

  Faq(this.topic, this.description, this.questions);

  Faq.fromJson(Map<String, dynamic> json)
      : topic = json['topic'],
        description = json['description'],
        questions = json['questions']
            .map<Question>((json) => Question.fromJson(json))
            .toList();
}
