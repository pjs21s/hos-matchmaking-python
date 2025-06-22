import collections
from typing import Dict, List, Deque, Optional

from matchmaking.domain.models import Player, Role, Match


class MatchmakingService:
    def __init__(self):
        self.waiting_queues: Dict[Role, Deque[Player]] = {role: collections.deque() for role in Role}
        print("MatchmakingService가 준비되었습니다.")
    
    def add_player_to_queue(self, player: Player):
        """생성된 플레이어 객체를 받아 대기열에 추가"""

        self.waiting_queues[player.role].append(player)
        print(f"[플레이어 추가] {player.model_dump()} 님이 대기열에 참가했습니다.")

    def get_total_players(self) -> int:
        """현재 대기열의 모든 플레이어 수를 반환"""
        return sum(len(q) for q in self.waiting_queues.values())
    
    def _return_players_to_queue(self, players: List[Player]):
        """플레이어들을 다시 대기열의 맨 앞으로 복귀"""
        for player in reversed(players):
            self.waiting_queues[player.role].appendleft(player)

    def _find_and_form_one_team(self) -> Optional[List[Player]]:
        """(내부 함수) 1탱, 1힐, 3자유 역할 규칙으로 5인 팀 구성을 시도"""
        if self.get_total_players() < 5:
            return None
        if not self.waiting_queues[Role.TANK] or not self.waiting_queues[Role.HEALER]:
            return None
        
        team: List[Player] = []
        team.append(self.waiting_queues[Role.TANK].popleft())
        team.append(self.waiting_queues[Role.HEALER].popleft())

        flex_roles_order = [Role.ASSASSIN, Role.BRUISER]

        for _ in range(3):
            found_flex = False
            for role in flex_roles_order:
                if self.waiting_queues[role]:
                    team.append(self.waiting_queues[role].popleft())
                    found_flex = True
                    break
            if not found_flex:
                print("[실패] 자유 역할군 인원 부족. 플레이어들을 복귀")
                self._return_players_to_queue(team)
                return None
        
        print(f"[성공] 팀 구성 완료: {[p.model_dump() for p in team]}")
        return team

    def try_create_match(self) -> Optional[Match]:
        """
        10인 게임 생성을 시도하는 메인 메소드
        """
        if self.get_total_players() < 10:
            print(f"[실패] 전체 인원이 10명 미만입니다. (현재: {self.get_total_players()}명)")
            return None
        
        print("-> 최소 인원(10명) 충족. A팀 구성을 시작")
        team_a = self._find_and_form_one_team()
        if not team_a:
            print("-> A팀 구성 실패. 매칭을 중단")
            return None
        
        print(f"-> A팀 구성 성공: {[p.name for p in team_a]}")
        print("-> B팀 구성을 시작")
        team_b = self._find_and_form_one_team()

        if not team_b:
            print("-> B팀 구성 실패. 매칭을 중단")
            self._return_players_to_queue(team_a)
            return None
        
        print(f"-> B팀 구성 성공: {[p.name for p in team_b]}")

        # TODO: MMR 조정 위치
        print("양 팀 구성 완료 최종 게임 생성")
        return Match(team_a=team_a, team_b=team_b)
