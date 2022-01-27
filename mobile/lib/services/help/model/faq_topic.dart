enum FaqTopic { CEI_PENDENCY }

extension ParseToString on FaqTopic {
  String toShortString() {
    return this.toString().split('.').last;
  }
}