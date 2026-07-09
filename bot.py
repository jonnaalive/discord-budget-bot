"""
디스코드 가계부 봇
사용자가 "치킨, 25000원" 형식으로 메시지를 보내면
구글 시트에 자동으로 기록하는 봇
"""

import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands

from google_sheets import GoogleSheetsManager
from ai_classifier import AIClassifier
from config import get_necessity

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 환경 변수
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME')
FAMILY_SHEET_ID = os.getenv('FAMILY_SHEET_ID')
FAMILY_SHEET_NAME = os.getenv('FAMILY_SHEET_NAME')
FAMILY_CHANNEL_NAME = os.getenv('FAMILY_CHANNEL_NAME', 'family-budget')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class BudgetBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

        # 개인 가계부 시트
        self.sheets_manager = GoogleSheetsManager(GOOGLE_SHEET_ID, GOOGLE_SHEET_NAME)
        # 가족 가계부 시트
        self.family_sheets_manager = GoogleSheetsManager(FAMILY_SHEET_ID, FAMILY_SHEET_NAME)
        self.ai_classifier = AIClassifier(OPENAI_API_KEY)

    def get_sheets_manager(self, channel_name: str) -> GoogleSheetsManager:
        """채널 이름에 따라 적절한 시트 매니저 반환"""
        if channel_name == FAMILY_CHANNEL_NAME:
            return self.family_sheets_manager
        return self.sheets_manager

    def parse_message(self, text: str) -> dict:
        """
        메시지를 파싱하여 품목명과 금액을 추출
        형식: "치킨, 25000원" 또는 "치킨, 25000"
        """
        # 쉼표로 분리
        parts = [part.strip() for part in text.split(',')]

        if len(parts) != 2:
            return None

        item_name = parts[0]
        amount_str = parts[1]

        # 금액에서 숫자만 추출
        amount_match = re.search(r'(\d+)', amount_str)
        if not amount_match:
            return None

        amount = int(amount_match.group(1))

        return {
            'item_name': item_name,
            'amount': amount
        }

    async def on_ready(self):
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message):
        # 봇 자신의 메시지는 무시
        if message.author == self.user:
            return

        # 명령어 먼저 처리
        await self.process_commands(message)

        # 명령어가 아닌 일반 메시지만 가계부 처리
        ctx = await self.get_context(message)
        if ctx.valid:
            return

        message_text = message.content
        logger.info(f"Received message from {message.author}: {message_text}")

        # 메시지 파싱
        parsed = self.parse_message(message_text)

        if not parsed:
            # 쉼표가 포함된 메시지인데 파싱 실패한 경우에만 안내
            if ',' in message_text:
                await message.channel.send(
                    "올바른 형식으로 입력해주세요.\n"
                    "예시: 치킨, 25000원"
                )
            return

        item_name = parsed['item_name']
        amount = parsed['amount']

        # AI로 대분류 자동 분류
        category = self.ai_classifier.classify(item_name)

        # 필수 여부 판단
        necessity = get_necessity(category)

        # 현재 날짜
        current_date = datetime.now().strftime('%Y-%m-%d')

        # 채널에 맞는 시트 매니저 선택
        sheets = self.get_sheets_manager(message.channel.name)
        is_family = message.channel.name == FAMILY_CHANNEL_NAME

        # 채널별 다른 시트 구조로 데이터 추가
        try:
            if is_family:
                # 가족 시트: A-날짜, B-소비형태(대분류), C-종류(품목명), D-가격
                sheets.append_row([
                    current_date,
                    category,
                    item_name,
                    amount,
                ])
            else:
                # 개인 시트: A-날짜, B-금액, C-품목명, D-대분류, E-필수여부
                sheets.append_row([
                    current_date,
                    amount,
                    item_name,
                    category,
                    necessity,
                ])

            # 성공 메시지
            await message.channel.send(
                f"✅ 기록 완료!\n\n"
                f"📅 날짜: {current_date}\n"
                f"💰 금액: {amount:,}원\n"
                f"🛒 품목: {item_name}\n"
                f"📁 대분류: {category}"
                + (f"\n⚡ 필수여부: {necessity}" if not is_family else "")
            )

            logger.info(f"Successfully recorded: {item_name} - {amount}원")

        except Exception as e:
            logger.error(f"Error recording to Google Sheets: {e}")
            await message.channel.send(
                f"❌ 기록 중 오류가 발생했습니다.\n"
                f"오류 내용: {str(e)}"
            )


bot = BudgetBot()


@bot.command(name='start')
async def start_command(ctx: commands.Context):
    """!start 명령어 처리"""
    await ctx.send(
        "안녕하세요! 가계부 봇입니다. 💰\n\n"
        "사용 방법:\n"
        "품목명, 금액 형식으로 입력해주세요.\n\n"
        "예시:\n"
        "치킨, 25000원\n"
        "택시, 15000\n\n"
        "자동으로 대분류와 필수 여부가 분류됩니다!"
    )


@bot.command(name='help')
async def help_command(ctx: commands.Context):
    """!help 명령어 처리"""
    await ctx.send(
        "📖 가계부 봇 도움말\n\n"
        "💡 사용법:\n"
        "품목명, 금액\n\n"
        "예시:\n"
        "• 치킨, 25000원\n"
        "• 스타벅스, 6500\n"
        "• 택시, 15000원\n\n"
        "자동 분류되는 항목:\n"
        "• 대분류: AI가 자동으로 9개 카테고리 중 분류\n"
        "• 필수 여부: 대분류에 따라 자동 판단\n\n"
        "📊 데이터는 구글 시트에 자동 기록됩니다."
    )


def main():
    """봇 실행"""
    if not DISCORD_BOT_TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN이 설정되지 않았습니다.")
    if not GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID가 설정되지 않았습니다.")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

    logger.info("Starting Budget Bot...")
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    main()
