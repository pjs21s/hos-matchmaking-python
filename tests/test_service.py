import pytest

from matchmaking.data.roster import CharacterRoster
from matchmaking.data.player_repository import PlayerRepository
from matchmaking.service.matchmaking_service import MatchmakingService
from matchmaking.domain.models import Role, Match, Player
from matchmaking.core.config import PLAYERS_PER_TEAM

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

# --- MMR 관련 로직 단위 테스트 ---

def test_calculate_average_mmr(matchmaking_service: MatchmakingService):
    """팀의 평귱 MMR 계산 로직 검증"""
    team1 = [
        Player(id=1, name="A", role=Role.TANK, mmr=1000),
        Player(id=2, name="B", role=Role.HEALER, mmr=2000),
        Player(id=3, name="C", role=Role.ASSASSIN, mmr=3000),
    ]
    team2_empty = []
    team3_single = [Player(id=4, name="D", role=Role.BRUISER, mmr=2500)]

    avg_mmr1 = matchmaking_service._calculate_team_avg_mmr(team1)
    avg_mmr2 = matchmaking_service._calculate_team_avg_mmr(team2_empty)
    avg_mmr3 = matchmaking_service._calculate_team_avg_mmr(team3_single)

    assert avg_mmr1 == 2000.0
    assert avg_mmr2 == 0.0
    assert avg_mmr3 == 2500.0

def test_team_balance_check(matchmaking_service: MatchmakingService):
    """두 팀 간의 밸런스가 맞는지 확인하는 로직을 검증"""

    team_a_balanced = [Player(id=1, name="A", role=Role.TANK, mmr=2000)]
    team_b_balanced = [Player(id=2, name="B", role=Role.HEALER, mmr=2050)]

    team_a_unbalanced = [Player(id=3, name="C", role=Role.TANK, mmr=2000)]
    team_b_unbalanced = [Player(id=4, name="D", role=Role.HEALER, mmr=2200)]
    
    team_a_boundary = [Player(id=5, name="E", role=Role.TANK, mmr=2000)]
    team_b_boundary = [Player(id=6, name="F", role=Role.HEALER, mmr=2100)]

    assert matchmaking_service._are_teams_balanced(team_a_balanced, team_b_balanced) is True
    assert matchmaking_service._are_teams_balanced(team_a_unbalanced, team_b_unbalanced) is False
    assert matchmaking_service._are_teams_balanced(team_a_boundary, team_b_boundary) is True

# --- 팀 생성 내부 메소드에 대한 단위 테스트 ---

def test__find_and_form_one_team_successful(matchmaking_service: MatchmakingService, player_repo: PlayerRepository):
    """5인 팀이 성공적으로 구성되는지 테스트"""
    player_ids = [1, 11, 21, 22, 31]  # 탱커, 힐러, 암살자2, 투사1
    for pid in player_ids:
        matchmaking_service.add_player_to_queue(player_repo.create_player(pid))
    
    team = matchmaking_service._find_and_form_one_team()

    assert team is not None
    assert len(team) == PLAYERS_PER_TEAM
    assert matchmaking_service.get_total_players() == 0

def test__find_and_form_one_team_fails_without_healer(matchmaking_service: MatchmakingService, player_repo: PlayerRepository):
    """ 힐러가 없을 때 5인 팀 구성이 실패하는지 테스트"""
    player_ids = [1, 21, 22, 31, 32] # 힐러 없음
    for pid in player_ids:
        matchmaking_service.add_player_to_queue(player_repo.create_player(pid))
    
    team = matchmaking_service._find_and_form_one_team()

    assert team is None
    assert matchmaking_service.get_total_players() == 5


# --- 매칭 메소드에 대한 통합 테스트 ---

def test_successful_match_creation(matchmaking_service: MatchmakingService, player_repo: PlayerRepository):
    """(통합 테스트) 조건이 완벽히 충족되었을 때 10인 게임이 성공적으로 생성되는지 테스트"""
    player_ids = [
        # 필수 역할군 (총 4명)
        1, 2,      # TANK
        11, 12,    # HEALER

        # 자유 역할군 (총 6명)
        21, 22, 23, 24, # ASSASSIN
        31, 32         # BRUISER
    ]
    
    for pid in player_ids:
        p = player_repo.create_player(character_id=pid)
        if p:
            matchmaking_service.add_player_to_queue(p)

    assert matchmaking_service.get_total_players() == 10

    match = matchmaking_service.try_create_match()

    assert match is not None, "10명의 조건이 완벽하므로 매칭은 성공해야 합니다."
    assert isinstance(match, Match)

    assert len(match.team_a) == PLAYERS_PER_TEAM
    assert len(match.team_b) == PLAYERS_PER_TEAM

    # 매칭 후 남은 플레이어가 없어야 함
    assert matchmaking_service.get_total_players() == 0


def test_try_create_match_fails_and_rolls_back(matchmaking_service: MatchmakingService, player_repo: PlayerRepository):
    player_ids = [1, 2, 11, 21, 22, 23, 24, 25, 31, 32]

    for pid in player_ids:
        matchmaking_service.add_player_to_queue(player_repo.create_player(pid))
    
    initial_player_count = matchmaking_service.get_total_players()
    assert initial_player_count == 10

    match = matchmaking_service.try_create_match()

    assert match is None, "B팀 힐러가 부족하므로 매칭은 실패"
    assert matchmaking_service.get_total_players() == initial_player_count, "A팀 플레이어들은 큐로 복귀해야 한다."