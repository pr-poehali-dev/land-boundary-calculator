import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Get cadastral plot data from NSPD API directly
    Args: event with httpMethod, queryStringParameters (cadastralNumber)
          context with request_id attribute
    Returns: HTTP response with plot data or error
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method != 'GET':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    params = event.get('queryStringParameters', {})
    cadastral_number = params.get('cadastralNumber', '')
    
    if not cadastral_number:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'cadastralNumber parameter is required'})
        }
    
    try:
        encoded_cn = urllib.parse.quote(cadastral_number)
        url = f'https://pkk.rosreestr.ru/api/features/1/{encoded_cn}'
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        req.add_header('Referer', 'https://pkk.rosreestr.ru/')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if not data or data.get('error'):
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Участок не найден',
                        'message': 'По данному кадастровому номеру объекты не найдены в базе Росреестра'
                    })
                }
            
            feature = data.get('feature', {})
            attrs = feature.get('attrs', {})
            
            area_value = 0
            if 'area_value' in attrs:
                try:
                    area_value = float(str(attrs['area_value']).replace(',', '.'))
                except:
                    area_value = 0
            
            points_count = max(4, int(area_value / 200) + 4) if area_value > 0 else 4
            cost_per_point = 3500 if area_value > 10000 else (4000 if area_value > 5000 else 4500)
            total_cost = points_count * cost_per_point
            
            coordinates = []
            extent = feature.get('extent', {})
            if extent:
                min_x = extent.get('xmin', 0)
                min_y = extent.get('ymin', 0)
                max_x = extent.get('xmax', 0)
                max_y = extent.get('ymax', 0)
                
                if min_x and min_y and max_x and max_y:
                    coordinates = [
                        [round(min_y, 6), round(min_x, 6)],
                        [round(max_y, 6), round(min_x, 6)],
                        [round(max_y, 6), round(max_x, 6)],
                        [round(min_y, 6), round(max_x, 6)]
                    ]
            
            address = attrs.get('address', 'Адрес не указан')
            if not address or address == 'None':
                address = f"Местоположение установлено относительно ориентира: {attrs.get('util_by_doc', 'Не указано')}"
            
            result = {
                'cadastralNumber': cadastral_number,
                'address': address,
                'area': round(area_value, 2),
                'category': attrs.get('category_type', 'Не указана'),
                'costPerPoint': cost_per_point,
                'pointsCount': points_count,
                'totalCost': total_cost,
                'coordinates': coordinates,
                'source': 'Росреестр ПКК'
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(result)
            }
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Участок не найден',
                    'message': 'Участок с таким кадастровым номером не найден в базе Росреестра'
                })
            }
        return {
            'statusCode': e.code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Ошибка API Росреестра',
                'message': f'Код ошибки: {e.code}'
            })
        }
    except urllib.error.URLError:
        return {
            'statusCode': 503,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Сервис временно недоступен',
                'message': 'Не удалось подключиться к API Росреестра'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Ошибка получения данных',
                'message': str(e)
            })
        }
