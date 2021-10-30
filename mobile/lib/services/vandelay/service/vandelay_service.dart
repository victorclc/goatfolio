

import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/vandelay/client/client.dart';

class VandelayService {
  final UserService userService;
  final VandelayClient client;

  VandelayService(this.userService) : client = VandelayClient(userService);

  Future<void> importCEIRequest(String username, String password) async {
    final importResponse = await client.importCEIRequest(username, password);
  }
}
