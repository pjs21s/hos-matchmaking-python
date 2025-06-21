from matchmaking.service import MatchmakingService, Role, Player

def test_add_player():
    """플레이어가 대기열에 정상적으로 추가된느지 테스트"""
    service = MatchmakingService()

    player = service.add_player(name="요한나", role=Role.TANK)

    assert player.id == 1
    assert player.name == "요한나"
    status = service.get_queue_status()
    assert len(status["TANK"]) == 1

def test_team_creation_fails_with_insufficient_players():
    """플레이어가 5명 미만일 때 팀 생성이 실패하는지 테스트"""
    service = MatchmakingService()
    service.add_player(name="요한나", role=Role.TANK)
    service.add_player(name="안두인", role=Role.HEALER)
    service.add_player(name="제이나", role=Role.ASSASSIN)

    team = service.try_create_team()

    assert team is None

def test_team_creation_fails_without_required_roles():
    """필수 역할군(탱커/힐러)이 없을 때 팀 생성이 실패하는지 테스트"""
    service = MatchmakingService()
    service.add_player(name="제이나", role=Role.ASSASSIN)
    service.add_player(name="레이너", role=Role.ASSASSIN)
    service.add_player(name="실바나스", role=Role.ASSASSIN)
    service.add_player(name="소냐", role=Role.BRUISER)
    service.add_player(name="데하카", role=Role.BRUISER)

    team = service.try_create_team()

    assert team is None

def test_successful_team_creation():
    """조건이 충족되었을 때 5인 팀이 성공적으로 생성되는지 테스트"""

    service = MatchmakingService()
    service.add_player(name="요한나", role=Role.TANK)
    service.add_player(name="알렉스트라자", role=Role.HEALER)
    service.add_player(name="제이나", role=Role.ASSASSIN)
    service.add_player(name="레이너", role=Role.ASSASSIN)
    service.add_player(name="소냐", role=Role.BRUISER)

    team = service.try_create_team()
    
    assert team is not None
    assert len(team) == 5

    roles_in_team = [player.role for player in team]
    assert roles_in_team.count(Role.TANK) == 1
    assert roles_in_team.count(Role.HEALER) == 1
