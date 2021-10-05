extension StringExtension on String {
  String capitalize() {
    return "${this[0].toUpperCase()}${this.substring(1)}";
  }

  String capitalizeWords() {
    final words = this.split(' ');
    String captalized = "";
    words.forEach((word) {
      if (captalized.isNotEmpty) {
        captalized += " ";
      }
      captalized += "${word[0].toUpperCase()}${word.substring(1)}";
    });
    return captalized;
  }
}
