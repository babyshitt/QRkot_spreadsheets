from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings


FORMAT = "%Y/%m/%d %H:%M:%S"

SPREADSHEET_BODY = {
    'properties': {'title': 'Отчет на текущую дату',
                   'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Лист1',
                               'gridProperties': {'rowCount': 100,
                                                  'columnCount': 11}}}]
}

PERMISSIONS_BODY = {
    'type': 'user', 'role': 'writer', 'emailAddress': settings.email
}

TABLE_VALUES = [
    ['Отчет от', 'текущей даты'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = {datetime.now().strftime(FORMAT)}
    SPREADSHEET_BODY['properties']['title'] = f'Отчет на {now_date_time}'
    service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=SPREADSHEET_BODY))
    return response['spreadsheetId']


async def set_user_permissions(
        spreadsheet_id: str, wrapper_services: Aiogoogle) -> None:
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id, json=PERMISSIONS_BODY, fields="id"))


async def spreadsheets_update_value(
        spreadsheet_id: str, projects: list,
        wrapper_services: Aiogoogle) -> None:
    now_date_time = {datetime.now().strftime(FORMAT)}
    TABLE_VALUES[0] = ['Отчёт от', now_date_time]
    new_table_values = TABLE_VALUES
    service = await wrapper_services.discover('sheets', 'v4')
    for res in projects:
        new_row = [res['name'], str(res['delta']), res['description']]
        new_table_values.append(new_row)
    update_body = {'majorDimension': 'ROWS', 'values': new_table_values}
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body))
