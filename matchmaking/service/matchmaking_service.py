import collections, logging
from typing import Dict, List, Deque, Optional

from matchmaking.domain.models import Player, Role, Match
from matchmaking.core.config import PLAYERS_PER_TEAM, FLEX_ROLES_PER_TEAM, PLAYERS_PER_MATCH

logger = logging.getLogger(__name__)

class MatchmakingService:
    def __init__(self):
        self.waiting_queues: Dict[Role, Deque[Player]] = {role: collections.deque() for role in Role}
        logger.info("MatchmakingService가 준비되었습니다.")
    
    def add_player_to_queue(self, player: Player):
        """생성된 플레이어 객체를 받아 대기열에 추가"""

        self.waiting_queues[player.role].append(player)
        logger.info(f"[플레이어 추가] {player.model_dump()} 님이 대기열에 참가했습니다.")

    def get_total_players(self) -> int:
        """현재 대기열의 모든 플레이어 수를 반환"""
        return sum(len(q) for q in self.waiting_queues.values())
    
    def _return_players_to_queue(self, players: List[Player]):
        """플레이어들을 다시 대기열의 맨 앞으로 복귀"""
        for player in reversed(players):
            self.waiting_queues[player.role].appendleft(player)

    def _find_and_form_one_team(self) -> Optional[List[Player]]:
        """(내부 함수) 1탱, 1힐, 3자유 역할 규칙으로 5인 팀 구성을 시도"""
        if self.get_total_players() < PLAYERS_PER_TEAM:
            return None
        if not self.waiting_queues[Role.TANK] or not self.waiting_queues[Role.HEALER]:
            return None
        
        team: List[Player] = []
        team.append(self.waiting_queues[Role.TANK].popleft())
        team.append(self.waiting_queues[Role.HEALER].popleft())

        flex_roles_order = [Role.ASSASSIN, Role.BRUISER]

        for _ in range(FLEX_ROLES_PER_TEAM):
            found_flex = False
            for role in flex_roles_order:
                if self.waiting_queues[role]:
                    team.append(self.waiting_queues[role].popleft())
                    found_flex = True
                    break
            if not found_flex:
                logger.warning("[실패] 자유 역할군 인원 부족. 플레이어들을 복귀")
                self._return_players_to_queue(team)
                return None
        
        logger.info(f"[성공] 팀 구성 완료: {[p.model_dump() for p in team]}")
        return team
    
    def _calculate_team_avg_mmr(self, team: List[Player]) -> float:
        """팀의 평균 MMR을 계산"""
        if not team:
            return 0.0
        total_mmr = sum(player.mmr for player in team)
        return total_mmr / len(team)
    
    def _are_teams_balanced(self, team_a: List[Player], team_b: List[Player]) -> bool:
        """두 팀의 MMR 밸런스가 허용 범위 내인지 확인"""
        avg_mmr_a = self._calculate_team_avg_mmr(team_a)
        avg_mmr_b = self._calculate_team_avg_mmr(team_b)

        mmr_difference_threshold = 100

        logger.info(f" -> 밸런스 확인: A팀 평균 MMR({avg_mmr_a:.2f}) vs B팀 평균 MMR({avg_mmr_b:.2f})")

        if abs(avg_mmr_a - avg_mmr_b) > mmr_difference_threshold:
            logger.warning("불균형")
            # TODO: 플레이어 교환 로직 추가하여 밸런스 맞추기 시도
            return False
        
        return True

    def try_create_match(self) -> Optional[Match]:
        """
        10인 게임 생성을 시도하는 메인 메소드
        """
        if self.get_total_players() < PLAYERS_PER_MATCH:
            logger.warning(f"[실패] 전체 인원이 10명 미만입니다. (현재: {self.get_total_players()}명)")
            return None
        
        logger.info("-> 최소 인원(10명) 충족. A팀 구성을 시작")
        team_a = self._find_and_form_one_team()
        if not team_a:
            logger.warning("-> A팀 구성 실패. 매칭을 중단")
            return None
        
        logger.info(f"-> A팀 구성 성공: {[p.name for p in team_a]}")
        logger.info("-> B팀 구성을 시작")
        team_b = self._find_and_form_one_team()

        if not team_b:
            logger.warning("-> B팀 구성 실패. 매칭을 중단")
            self._return_players_to_queue(team_a)
            return None
        
        logger.info(f"-> B팀 구성 성공: {[p.name for p in team_b]}")

        if not self._are_teams_balanced(team_a, team_b):
            logger.warning("최종 매칭 실패, 대기열로 복귀")
            self._return_players_to_queue(team_a)
            self._return_players_to_queue(team_b)
            return None
        
        logger.info("양 팀 구성 완료 최종 게임 생성")
        return Match(team_a=team_a,
                     team_b=team_b,
                     avg_mmr_a=self._calculate_team_avg_mmr(team_a),
                     avg_mmr_b=self._calculate_team_avg_mmr(team_b),
                     )
