import json
from typing import Dict, List, Optional

from matchmaking.domain.models import CharacterTemplate

class CharacterRoster:
    """
    characters.json 파일을 읽어 캐릭터 목록을 관리
    """
    def __init__(self, data_path: str = "characters.json"):
        self._templates: Dict[int, CharacterTemplate] = {}
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                for data in character_data:
                    template = CharacterTemplate(**data)
                    self._templates[template.id] = template
            print(f"CharacterRoster가 준비되었습니다. {len(self._templates)}개의 캐릭터 정보를 읽었습니다.")
        except FileNotFoundError:
            print(f"[오류] 캐릭터 데이터 파일({data_path})을 찾을 수 없습니다.")
    
    def get_all_characters(self) -> List[CharacterTemplate]:
        """모든 캐릭터 리스트를 반환"""
        return list(self._templates.values())
    
    def get_character_by_id(self, character_id: int) -> Optional[CharacterTemplate]:
        """캐릭터 ID로 찾습니다."""
        return self._templates.get(character_id)
