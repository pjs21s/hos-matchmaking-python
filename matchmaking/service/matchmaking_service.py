import collections
from typing import Dict, List, Deque, Optional

from matchmaking.domain.models import Player, Role


class MatchmakingService:
    def __init__(self):
        self.waiting_queues: Dict[Role, Deque[Player]] = {role: collections.deque() for role in Role}
        print("MatchmakingService가 준비되었습니다.")

    def get_queue_status(self) -> Dict[str, list]:
        """디버깅을 위해 현재 대기열 상태를 반환"""
        status = {}
        for role, queue in self.waiting_queues.items():
            status[role.value] = [player.model_dump() for player in queue]
        return status
    
    def add_player_to_queue(self, player: Player):
        """생성된 플레이어 객체를 받아 대기열에 추가"""

        self.waiting_queues[player.role].append(player)
        print(f"[플레이어 추가] {player.model_dump()} 님이 대기열에 참가했습니다.")

    def try_create_team(self) -> Optional[List[Player]]:
        """1탱, 1힐, 3자유 역할 규칙으로 5인 팀 구성을 시도"""
        print("\n[매칭 시도] 팀 구성을 시작...")
        for role, queue in self.waiting_queues.items():
            print(f" - {role.value:<10}: {len(queue)}명 대기중")
        
        total_players = sum(len(q) for q in self.waiting_queues.values())
        if total_players < 5:
            print("[실패] 전체 인원이 5명 미만입니다.")
            return None

        tank_queue = self.waiting_queues[Role.TANK]
        healer_queue = self.waiting_queues[Role.HEALER]

        if not tank_queue or not healer_queue:
            print("[실패] 필수 역할군(탱커 또는 힐러)이 부족합니다.")
            return None
    
        team: List[Player] = []
        team.append(tank_queue.popleft())
        team.append(healer_queue.popleft())

        flex_roles_order = [Role.ASSASSIN, Role.BRUISER, Role.HEALER, Role.TANK]

        for _ in range(3):
            found_flex = False
            for role in flex_roles_order:
                if self.waiting_queues[role]:
                    team.append(self.waiting_queues[role].popleft())
                    found_flex = True
                    break
            if not found_flex:
                print("[실패] 자유 역할군 인원 부족. 플레이어들을 복귀")
                for player in reversed(team):
                    self.waiting_queues[player.role].appendleft(player)
                return None
        
        print(f"[성공] 팀 구성 완료: {[p.model_dump() for p in team]}")
        return team
