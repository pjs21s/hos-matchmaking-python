import random
from matchmaking.data.roster import CharacterRoster
from matchmaking.data.player_repository import PlayerRepository
from matchmaking.service.matchmaking_service import MatchmakingService

def run_test_scenario():
    """
    매치메이킹 시나리오를 실행하는 테스트 함수
    """

    print("--- 매치메이킹 시뮬레이션 시작 --- \n")
    roster = CharacterRoster(data_path="characters.json")
    player_repo = PlayerRepository(roster=roster)
    matchmaking_service = MatchmakingService()

    print("\n[1단계] 로스터에서 캐릭터를 선택하여 플레이어를 생성하고 대기열에 추가")

    tank_chars = [c for c in roster.get_all_characters() if c.role.value == "TANK"]
    healer_chars = [c for c in roster.get_all_characters() if c.role.value == "HEALER"]
    other_chars = [c for c in roster.get_all_characters() if c.role.value not in ["TANK", "HEALER"]]

    player_one = player_repo.create_player(character_id=random.choice(tank_chars).id)
    matchmaking_service.add_player_to_queue(player_one)

    player_two = player_repo.create_player(character_id=random.choice(healer_chars).id)
    matchmaking_service.add_player_to_queue(player_two)

    for _ in range(3):
        random_char = random.choice(other_chars)
        p = player_repo.create_player(character_id=random_char.id)
        matchmaking_service.add_player_to_queue(p)
        other_chars.remove(random_char)

    print("\n[2단계] 매칭을 시도합니다.")
    team = matchmaking_service.try_create_team()

    if team:
        print("최종 매칭 성공! 생성된 팀 아래와 같음")
        for player in team:
            print(f" - {player.model_dump()}")
    else:
        print("최종 매칭 실패")
    
    print("\n --- 매치메이킹 시뮬레이션 종료 ---")

if __name__ == "__main__":
    run_test_scenario()