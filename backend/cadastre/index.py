import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Get cadastral plot data from NSPD API
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
    
    cleaned_number = cadastral_number.replace(':', ':')
    nspd_url = f'https://nspd.gov.ru/api/geoportal/v2/search/geoportal?thematicSearchId=1&query={cleaned_number}'
    
    try:
        req = urllib.request.Request(nspd_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if not data.get('data') or not data['data'].get('features'):
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Участок не найден в НСПД',
                        'message': 'Возможно, объект снят с учета или указан неверный кадастровый номер'
                    })
                }
            
            features = data['data']['features']
            if not features:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Участок не найден',
                        'message': 'По данному кадастровому номеру объекты не найдены'
                    })
                }
            
            feature = features[0]
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            coordinates = []
            if geometry.get('type') == 'Polygon' and geometry.get('coordinates'):
                coords_array = geometry['coordinates'][0]
                coordinates = [[round(c[1], 6), round(c[0], 6)] for c in coords_array[:4]]
            
            area = properties.get('area', 0)
            if isinstance(area, str):
                try:
                    area = float(area.replace(',', '.'))
                except:
                    area = 0
            
            points_count = max(4, int(area / 200) + 4) if area > 0 else 4
            cost_per_point = 3500 if area > 10000 else (4000 if area > 5000 else 4500)
            total_cost = points_count * cost_per_point
            
            result = {
                'cadastralNumber': cadastral_number,
                'address': properties.get('address', 'Адрес не указан'),
                'area': round(area, 2),
                'category': properties.get('category', 'Не указана'),
                'costPerPoint': cost_per_point,
                'pointsCount': points_count,
                'totalCost': total_cost,
                'coordinates': coordinates,
                'source': 'NSPD'
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
        return {
            'statusCode': e.code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Ошибка API NSPD',
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
                'message': 'Не удалось подключиться к API NSPD'
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
                'error': 'Внутренняя ошибка сервера',
                'message': str(e)
            })
        }
