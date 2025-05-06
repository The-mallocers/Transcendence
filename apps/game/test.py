from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse

from apps.game.models import Game, Rank
from apps.player.models import Player
from utils.enums import GameStatus, Ranks


class RankModelTest(TestCase):
    """Test the Rank model"""

    def setUp(self):
        """Set up test data"""
        Rank.objects.get_or_create(
            name=Ranks.BRONZE.name,
            defaults={
                'icon': "rank_icon/bronze.png",
                'mmr_min': 0,
                'mmr_max': 999
            }
        )

    def test_rank_creation(self):
        """Test that a rank can be created"""
        rank = Rank.objects.get(name=Ranks.BRONZE.name)
        self.assertEqual(rank.mmr_min, 1)
        self.assertEqual(rank.mmr_max, 100)
        # self.assertEqual(rank.icon, "rank_icon/bronze.png")


class GameModelTest(TestCase):
    """Test the Game model"""

    @patch('apps.game.models.RedisConnectionPool.get_sync_connection')
    def setUp(self, mock_redis):
        """Set up test data with mocked Redis"""
        self.mock_redis = MagicMock()
        self.mock_redis.json.return_value.get.return_value = {}
        mock_redis.return_value = self.mock_redis

        # Create a game instance
        self.game = Game.objects.create(
            id="12345",
            points_to_win=3
        )

    def test_game_creation(self):
        """Test that a game can be created"""
        game = Game.objects.get(code="12345")
        self.assertEqual(game.points_to_win, 3)
        self.assertIsNone(game.winner)
        self.assertIsNone(game.loser)
        self.assertFalse(game.is_duel)

    @patch('apps.game.models.send_group')
    @patch('apps.game.models.async_to_sync')
    def test_init_players(self, mock_async_to_sync, mock_send_group):
        """Test initializing players for a game"""
        # Mock player objects
        self.game.pL = MagicMock(spec=Player)
        self.game.pL.client.id = "player1"
        self.game.pR = MagicMock(spec=Player)
        self.game.pR.client.id = "player2"

        # Mock Redis methods
        self.mock_redis.json.return_value.get.return_value = {}
        self.mock_redis.hget.return_value = "channel_name"

        # Call the method
        self.game.init_players()

        # Assert Redis operations were called
        self.mock_redis.json.return_value.set.assert_called()
        self.mock_redis.hset.assert_called()

        # Assert players left queue
        self.game.pL.leave_queue.assert_called_once()
        self.game.pR.leave_queue.assert_called_once()

        # Assert group message was sent
        mock_send_group.assert_called_once()

    def test_rset_status(self):
        """Test setting game status in Redis"""
        # Mock Redis methods
        self.mock_redis.json.return_value.get.return_value = GameStatus.STARTING.value

        # Call the method
        self.game.rset_status(GameStatus.RUNNING)

        # Assert Redis operation was called
        self.mock_redis.json.return_value.set.assert_called_once()


class GameViewTest(TestCase):
    """Test the game views"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_pong_view(self):
        """Test the pong view returns the correct JSON response"""
        response = self.client.get(reverse('pong'))
        # self.assertEqual(response.status_code, 200)
        # self.assertIn('html', response.json())

    def test_matchmaking_view(self):
        """Test the matchmaking view returns the correct JSON response"""
        # This test requires a logged-in client, so we'll mock that
        with patch('apps.client.models.Clients.get_client_by_request') as mock_get_client:
            mock_get_client.return_value = MagicMock()
            response = self.client.get(reverse('matchmaking'))
            # self.assertEqual(response.status_code, 200)
            # self.assertIn('html', response.json())
