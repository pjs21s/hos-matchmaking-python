import random
from matchmaking.data.roster import CharacterRoster
from matchmaking.data.player_repository import PlayerRepository
from matchmaking.service.matchmaking_service import MatchmakingService

def run_10_player_scenario():
    print("--- 10인 매치 시뮬레이션 시작 ---\n")

    roster = CharacterRoster(data_path="characters.json")
    player_repo = PlayerRepository(roster=roster)
    matchmaking_service = MatchmakingService()

    print("\n[1단계] 12명의 플레이어를 대기열에 추가")
    
    all_character_ids = [c.id for c in roster.get_all_characters()]
    
    try:
        selected_ids = random.sample(all_character_ids, 12)
    except ValueError:
        print("[오류] characters.json에 정의된 캐릭터가 12명보다 적다.")
        return

    for char_id in selected_ids:
        # ID를 사용해 플레이어를 생성하고 큐에 추가.
        player = player_repo.create_player(character_id=char_id)
        if player:
            matchmaking_service.add_player_to_queue(player)

    # 3. 10인 매칭 시도
    match = matchmaking_service.try_create_match()

    # 4. 결과 확인
    if match:
        print("\n=========================================")
        print("최종 매칭 성공! 10인 게임이 생성")
        print(f"  - TEAM A: {[p.name for p in match.team_a]}")
        print(f"  - TEAM B: {[p.name for p in match.team_b]}")
        print("=========================================")
        print(f"남은 대기 인원: {matchmaking_service.get_total_players()}명")
    else:
        print("\n=========================================")
        print("최종 매칭 실패.")
        print(f"남은 대기 인원: {matchmaking_service.get_total_players()}명")
        print("=========================================")

if __name__ == "__main__":
    run_10_player_scenario()
