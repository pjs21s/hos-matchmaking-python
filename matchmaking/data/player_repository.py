import random
from typing import Dict, Optional

from matchmaking.domain.models import Player
from matchmaking.data.roster import CharacterRoster

class PlayerRepository:
    def __init__(self, roster: CharacterRoster):
        self._players: Dict[int, Player] = {}
        self._next_player_id = 1
        self.roster = roster
        print("PlayerRepostiory 준비")

    def create_player(self, character_id: int) -> Optional[Player]:
        """캐릭터 ID를 받아 해당 캐릭터 정보를 가진 플레이어 인스턴스 생성"""
        character_template = self.roster.get_character_by_id(character_id)
        if not character_template:
            print(f"[Repository 오류] ID {character_id}에 해당하는 캐릭터가 없습니다.")
            return None
        
        # Random MMR 생성
        player_mmr = random.randint(1500, 3500)
    
        new_player = Player(
            id=self._next_player_id,
            name=character_template.name,
            role=character_template.role,
            mmr=player_mmr
        )

        self._players[self._next_player_id] = new_player
        self._next_player_id += 1
        print(f"[Repository] 플레이어 생성: {new_player.model_dump()}")
        return new_player
