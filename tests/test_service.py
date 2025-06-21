import pytest

from matchmaking.data.roster import CharacterRoster
from matchmaking.data.player_repository import PlayerRepository
from matchmaking.service.matchmaking_service import MatchmakingService
from matchmaking.domain.models import Role

# --- Pytest Fixture: 테스트를 위한 준비 과정을 도와줌

@pytest.fixture
def roster() -> CharacterRoster:
    """테스트용 캐릭터 객체를 생성"""
    return CharacterRoster(data_path="characters.json")

@pytest.fixture
def player_repo(roster: CharacterRoster) -> PlayerRepository:
    """
    테스트용 플레이어 객체를 생성
    roster fixture를 주입 받아 사용
    """
    return PlayerRepository(roster=roster)

@pytest.fixture
def matchmaking_service() -> MatchmakingService:
    """테스트할 대상인 매치메이킹 서비스 객체를 생성"""
    return MatchmakingService()


# -- 실제 테스트 케이스 ---

def test_team_creation_fails_with_insufficient_players(matchmaking_service: MatchmakingService, player_repo: PlayerRepository):
    """플레이어가 5명 미만일 때 팀 생성이 실패하는지 테스트"""
    player_one = player_repo.create_player(character_id=1)
    player_two = player_repo.create_player(character_id=11)
    matchmaking_service.add_player_to_queue(player_one)
    matchmaking_service.add_player_to_queue(player_two)

    team = matchmaking_service.try_create_team()

    assert team is None

def test_successful_team_creation(matchmaking_service: MatchmakingService, player_repo: PlayerRepository):
    """조건이 충족되었을 때 5인 팀이 성공적으로 생성되는지 테스트"""
    player_one = player_repo.create_player(character_id=1)
    player_two = player_repo.create_player(character_id=11)
    player_three = player_repo.create_player(character_id=21)
    player_four = player_repo.create_player(character_id=22)
    player_five = player_repo.create_player(character_id=31)

    players = [player_one, player_two, player_three, player_four, player_five]
    for p in players:
        matchmaking_service.add_player_to_queue(p)

    team = matchmaking_service.try_create_team()

    assert team is not None
    assert len(team) == 5
    roles_in_team = [player.role for player in team]
    assert roles_in_team.count(Role.TANK) == 1
    assert roles_in_team.count(Role.HEALER) == 1

def test_team_creation_returns_players_on_flex_failure(matchmaking_service: MatchmakingService, player_repo: PlayerRepository):
    """자유 역할군이 부족하여 팀 구성 실패 시, 뽑았던 탱/힐을 큐로 복귀시키는지 테스트"""

    player_one = player_repo.create_player(character_id=1)
    player_two = player_repo.create_player(character_id=11)
    
    matchmaking_service.add_player_to_queue(player_one)
    matchmaking_service.add_player_to_queue(player_two)
    
    initial_status = matchmaking_service.get_queue_status()
    assert len(initial_status["TANK"]) == 1
    assert len(initial_status["HEALER"]) == 1

    team = matchmaking_service.try_create_team()

    assert team is None

    final_status = matchmaking_service.get_queue_status()
    assert len(final_status["TANK"]) == 1, "탱커가 큐로 복귀해야 합니다."
    assert len(final_status["HEALER"]) == 1, "힐러가 큐로 복귀해야 합니다."
