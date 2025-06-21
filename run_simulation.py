from matchmaking.service import MatchmakingService, Role

def run_test_scenario():
    """
    매치메이킹 시나리오를 실행하는 테스트 함수
    """

    print("--- 매치메이킹 시뮬레이션 시작 --- \n")

    service = MatchmakingService()

    print("\n[1단계] 테스트 플레이어들을 대기열에 추가합니다.")
    service.add_player(name="요한나", role=Role.TANK)
    service.add_player(name="알렉스트라자", role=Role.HEALER)
    service.add_player(name="제이나", role=Role.ASSASSIN)
    service.add_player(name="레이너", role=Role.ASSASSIN)

    print("\n --- 첫 번째 매칭 시도 (실패 예상) ---")
    service.try_create_team()

    print("\n[2단계] 5번째 플레이어를 추가")
    service.add_player(name="소냐", role=Role.BRUISER)

    print("\n --- 두 번째 매칭 시도 (성공 예상) ---")
    team = service.try_create_team()

    print("\n[3단계] 최종 결과 확인")
    if team:
        print("최종 매칭 성공! 생성된 팀 아래와 같음")
        for player in team:
            print(f" - {player.dict()}")
    else:
        print("최종 매칭 실패")
    
    print("\n --- 매치메이킹 시뮬레이션 종료 ---")

if __name__ == "__main__":
    run_test_scenario()