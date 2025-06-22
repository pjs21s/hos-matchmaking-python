import logging

logging.basicConfig(
    level=logging.INFO,  # INFO 레벨 이상의 로그를 출력하도록 설정
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# TODO: 의존성 주입, API 엔드포인트 정의 필요