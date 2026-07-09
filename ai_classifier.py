"""
AI 기반 자동 분류 모듈
OpenAI API를 사용하여 품목명을 대분류 카테고리로 자동 분류
"""

from openai import OpenAI
from config import CATEGORIES


class AIClassifier:
    """
    AI 기반 품목 분류기
    """

    def __init__(self, api_key: str):
        """
        초기화

        Args:
            api_key: OpenAI API 키
        """
        self.client = OpenAI(api_key=api_key)
        self.categories = CATEGORIES

    def classify(self, item_name: str) -> str:
        """
        품목명을 받아서 대분류 카테고리로 분류

        Args:
            item_name: 품목명 (예: "치킨", "스타벅스 커피")

        Returns:
            대분류 카테고리 (예: "비필수 식비", "필수 소비")
        """
        # 카테고리 목록을 문자열로 변환
        categories_str = "\n".join([f"- {cat}" for cat in self.categories])

        # AI에게 분류 요청
        prompt = f"""다음 품목명을 가계부 대분류 카테고리로 분류해주세요.

품목명: {item_name}

가능한 카테고리:
{categories_str}

분류 기준:
- 비필수 식비: 외식, 배달음식, 간식, 카페 등
- 필수 식비: 장보기, 마트, 식재료 등 생활 필수 식료품
- 필수 소비: 생활용품, 화장품, 세제, 주거비 등 생활 필수품
- 비필수 소비: 쇼핑, 옷, 신발, 액세서리 등 선택적 소비
- 콘텐츠: 영화, 책, 넷플릭스, 게임, 음악 등
- 네트워킹: 회식, 모임, 선물, 경조사비 등
- 의료비: 병원, 약국, 건강검진 등
- 공과금: 전기세, 수도세, 관리비, 통신비 등
- 기부금: 기부, 후원 등

위 카테고리 중 하나만 선택해서 카테고리 이름만 정확히 답변해주세요.
다른 설명 없이 카테고리 이름만 출력하세요."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 가계부 품목을 정확하게 분류하는 전문가입니다. "
                                   "주어진 카테고리 중에서 가장 적절한 하나를 선택해야 합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=50
            )

            category = response.choices[0].message.content.strip()

            # 응답이 유효한 카테고리인지 확인
            if category in self.categories:
                return category
            else:
                # 유효하지 않은 경우 기본값 반환
                print(f"Warning: AI returned invalid category '{category}'. Using default.")
                return "비필수 소비"

        except Exception as e:
            print(f"Error in AI classification: {e}")
            # 오류 발생 시 기본 카테고리 반환
            return "비필수 소비"
