import unittest
from unittest.mock import MagicMock

from application.models.friend import FriendRequest, RequestType, FriendsList, Friend
from application.models.user import User
from core import friend_request_handler


class TestFriendRequestHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.list_repository = MagicMock()
        self.push_client = MagicMock()
        self.user1 = User("1111", "Um", "um@gmail.com")
        self.user2 = User("2222", "Dois", "dois@gmail.com")

    def test_request_from_type_empty_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.FROM)
        self.list_repository.find_by_subject.return_value = FriendsList(request.to.sub)

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertIn(request.to, saved_list.invites)
        self.assertNotIn(request.to, saved_list.requests)
        self.assertNotIn(request.to, saved_list.friends)

    def test_request_from_type_already_on_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.FROM)
        self.list_repository.find_by_subject.return_value = FriendsList(self.user1.sub, invites=[Friend(request.to)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertIn(request.to, saved_list.invites)
        self.assertTrue(len(saved_list.invites) == 1)
        self.assertNotIn(request.to, saved_list.requests)
        self.assertNotIn(request.to, saved_list.friends)

    def test_request_to_type_empty_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.TO)
        self.list_repository.find_by_subject.return_value = FriendsList(request.from_.sub)

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_called_once()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.from_, saved_list.invites)
        self.assertIn(request.from_, saved_list.requests)
        self.assertNotIn(request.from_, saved_list.friends)

    def test_request_to_type_already_on_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.TO)
        self.list_repository.find_by_subject.return_value = FriendsList(request.from_.sub,
                                                                        requests=[Friend(request.from_)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.from_, saved_list.invites)
        self.assertTrue(len(saved_list.requests) == 1)
        self.assertIn(request.from_, saved_list.requests)
        self.assertNotIn(request.from_, saved_list.friends)

    def test_request_accept_from_type_empty_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.ACCEPT_FROM)
        self.list_repository.find_by_subject.return_value = FriendsList(request.to.sub,
                                                                        requests=[Friend(request.to)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.to, saved_list.invites)
        self.assertNotIn(request.to, saved_list.requests)
        self.assertIn(request.to, saved_list.friends)

    def test_request_accept_from_type_already_on_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.ACCEPT_FROM)
        self.list_repository.find_by_subject.return_value = FriendsList(request.to.sub,
                                                                        requests=[Friend(request.to)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.to, saved_list.invites)
        self.assertNotIn(request.to, saved_list.requests)
        self.assertIn(request.to, saved_list.friends)
        self.assertTrue(len(saved_list.friends) == 1)

    def test_request_accept_to_type_empty_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.ACCEPT_TO)
        self.list_repository.find_by_subject.return_value = FriendsList(request.from_.sub,
                                                                        invites=[Friend(request.from_)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_called_once()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.from_, saved_list.invites)
        self.assertNotIn(request.from_, saved_list.requests)
        self.assertIn(request.from_, saved_list.friends)

    def test_request_accept_to_type_already_on_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.ACCEPT_TO)
        self.list_repository.find_by_subject.return_value = FriendsList(request.from_.sub,
                                                                        friends=[Friend(request.from_)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.from_, saved_list.invites)
        self.assertNotIn(request.from_, saved_list.requests)
        self.assertIn(request.from_, saved_list.friends)
        self.assertTrue(len(saved_list.friends) == 1)

    def test_request_decline_from_type_empty_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.DECLINE_FROM)
        self.list_repository.find_by_subject.return_value = FriendsList(request.to.sub,
                                                                        requests=[Friend(request.to)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.to, saved_list.invites)
        self.assertNotIn(request.to, saved_list.requests)
        self.assertNotIn(request.to, saved_list.friends)

    def test_request_decline_to_type_empty_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.DECLINE_TO)
        self.list_repository.find_by_subject.return_value = FriendsList(request.to.sub,
                                                                        invites=[Friend(request.from_)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.to, saved_list.invites)
        self.assertNotIn(request.to, saved_list.requests)
        self.assertNotIn(request.to, saved_list.friends)

    def test_request_cancel_from_type_empty_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.CANCEL_FROM)
        self.list_repository.find_by_subject.return_value = FriendsList(request.to.sub,
                                                                        invites=[Friend(request.to)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.to, saved_list.invites)
        self.assertNotIn(request.to, saved_list.requests)
        self.assertNotIn(request.to, saved_list.friends)

    def test_request_cancel_to_type_empty_friend_list(self):
        request = FriendRequest(from_=self.user1, to=self.user2, type_=RequestType.CANCEL_TO)
        self.list_repository.find_by_subject.return_value = FriendsList(request.to.sub,
                                                                        requests=[Friend(request.from_)])

        friend_request_handler.friend_request_handler(request, self.list_repository, self.push_client)

        self.list_repository.save.assert_called_once()
        self.push_client.send.assert_not_called()
        saved_list: FriendsList = self.list_repository.save.call_args[0][0]
        self.assertNotIn(request.to, saved_list.invites)
        self.assertNotIn(request.to, saved_list.requests)
        self.assertNotIn(request.to, saved_list.friends)
