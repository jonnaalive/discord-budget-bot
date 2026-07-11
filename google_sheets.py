"""Google Sheets API integration."""

import json
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsManager:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, spreadsheet_id: str, sheet_name: str):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.service = self._get_service()

    def _get_service(self):
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        credentials_file = 'credentials.json'

        if credentials_json:
            credentials = Credentials.from_service_account_info(
                json.loads(credentials_json), scopes=self.SCOPES
            )
        elif os.path.exists(credentials_file):
            credentials = Credentials.from_service_account_file(
                credentials_file, scopes=self.SCOPES
            )
        else:
            raise FileNotFoundError(
                'GOOGLE_CREDENTIALS_JSON 환경변수 또는 credentials.json 파일이 필요합니다.'
            )

        return build('sheets', 'v4', credentials=credentials)

    def append_row(self, values: list):
        try:
            last_col = chr(ord('A') + len(values) - 1)
            return self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{self.sheet_name}'!A:{last_col}",
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [values]},
            ).execute()
        except HttpError as error:
            raise Exception(f'Google Sheets API 오류: {error}') from error

    def get_all_data(self):
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{self.sheet_name}'!A:E",
            ).execute()
            return result.get('values', [])
        except HttpError as error:
            raise Exception(f'Google Sheets API 오류: {error}') from error

    def clear_sheet(self):
        try:
            return self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A2:E',
            ).execute()
        except HttpError as error:
            raise Exception(f'Google Sheets API 오류: {error}') from error
