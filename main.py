import json
import requests
from bs4 import BeautifulSoup

url = 'https://booking.kai.id/'

def extract_source(url, params):
  headers = { 'User-Agent': 'Mozilla/5.0' }
  source = requests.get(url, headers=headers, params=params).text
  return source

def extract_data(source):
  soup = BeautifulSoup(source, 'lxml')
  data_wrapper = soup.find_all('div', class_='data-wrapper')
  result = list()

  for item in data_wrapper:
    train_name = item.find('div', class_='name').text
    train_class = item.find('div', class_='{kelas kereta}').text

    departure_station = item.find('div', class_='station-start').text
    departure_time = item.find('div', class_='time-start').text
    departure_date = item.find('div', class_='date-start').text

    arrival_card = item.find('div', class_='card-arrival')
    arrival_station = arrival_card.contents[1].text
    arrival_time = arrival_card.contents[3].text
    arrival_date = arrival_card.contents[5].text

    travel_time = item.find('div', class_='long-time').text
    ticket_price = item.find('div', class_='price').text
    seat_availability = item.find('small', class_='sisa-kursi').text

    data = {
      'train_name': train_name,
      'train_class': train_class,
      'travel_time': travel_time,
      'ticket_price': ticket_price,
      'seat_availability': seat_availability,
      'origin': {
        'departure_station': departure_station,
        'departure_date': departure_date,
        'departure_time': departure_time
      },
      'destination': {
        'arrival_station': arrival_station,
        'arrival_date': arrival_date,
        'arrival_time': arrival_time
      }
    }

    result.append(data)

  return result

def lambda_handler(event, context):
  try:
    origination = event['queryStringParameters']['from']
    destination = event['queryStringParameters']['to']
    tanggal = event['queryStringParameters']['date']
    params = {
      'origination': origination,
      'destination': destination,
      'tanggal': tanggal,
      'adult': '1',
      'infant': '0',
      'submit': 'Cari+%26+Pesan+Tiket'
    }
    status = 200
    data = extract_data(extract_source(url, params))
  except:
    status = 400
    data = {
      'message': 'Missing query parameters'
    }

  response = {
    'statusCode': status,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps(data)
  }
  return response
