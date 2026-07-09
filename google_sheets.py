"""
Google Sheets API 연동 모듈
"""

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsManager:
    """
    구글 시트 관리 클래스
    """

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, spreadsheet_id: str, sheet_name: str):
        """
        초기화

        Args:
            spreadsheet_id: 구글 시트 ID
            sheet_name: 시트 탭 이름
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.service = self._get_service()

    def _get_service(self):
        """
        Google Sheets API 서비스 인스턴스 생성
        """
        credentials_file = 'credentials.json'

        if not os.path.exists(credentials_file):
            raise FileNotFoundError(
                f"{credentials_file} 파일이 없습니다.\n"
                "구글 클라우드 콘솔에서 서비스 계정 키를 생성하고 "
                "credentials.json으로 저장해주세요."
            )

        credentials = Credentials.from_service_account_file(
            credentials_file,
            scopes=self.SCOPES
        )

        service = build('sheets', 'v4', credentials=credentials)
        return service

    def append_row(self, values: list):
        """
        시트 하단에 새로운 행 추가

        Args:
            values: 추가할 데이터 리스트 [날짜, 금액, 품목명, 대분류, 필수여부]
        """
        try:
            body = {
                'values': [values]
            }

            # 값 개수에 맞춰 범위 자동 설정
            last_col = chr(ord('A') + len(values) - 1)
            range_name = f"'{self.sheet_name}'!A:{last_col}"

            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return result

        except HttpError as error:
            raise Exception(f"Google Sheets API 오류: {error}")

    def get_all_data(self):
        """
        시트의 모든 데이터 조회
        """
        try:
            range_name = f"'{self.sheet_name}'!A:E"

            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()

            return result.get('values', [])

        except HttpError as error:
            raise Exception(f"Google Sheets API 오류: {error}")

    def clear_sheet(self):
        """
        시트 데이터 전체 삭제 (헤더 제외)
        """
        try:
            result = self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A2:E'
            ).execute()

            return result

        except HttpError as error:
            raise Exception(f"Google Sheets API 오류: {error}")
