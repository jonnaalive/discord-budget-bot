"""
Configuration for the Budget Bot
"""

# 대분류 카테고리 목록
CATEGORIES = [
    "비필수 식비",
    "필수 소비",
    "콘텐츠",
    "비필수 소비",
    "네트워킹",
    "의료비",
    "공과금",
    "기부금",
    "필수 식비"
]

# 필수 여부 판단 로직
def get_necessity(category: str) -> str:
    """
    대분류에 '필수'가 포함되면 '필수', 아니면 '비필수' 반환
    """
    return "필수" if "필수" in category else "비필수"

# 구글 시트 열 구조
# A열: 입력 날짜
# B열: 금액
# C열: 품목명
# D열: 대분류
# E열: 필수 여부
