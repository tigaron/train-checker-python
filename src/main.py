import re
import json
import requests
from bs4 import BeautifulSoup

url = 'https://booking.kai.id/'

def extract_source(url, params):
  try:
    headers = { 'User-Agent': 'Mozilla/5.0' }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
  except: raise
  return response.text

def extract_data(source):
  try: soup = BeautifulSoup(source, 'html.parser')
  except: raise
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

    result.append({
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
    })
  return result

def transform_month(string):
  month_data = {
    'JAN': 'Januari',
    'FEB': 'Februari',
    'MAR': 'Maret',
    'APR': 'April',
    'MAY': 'Mei',
    'JUN': 'Juni',
    'JUL': 'Juli',
    'AUG': 'Agustus',
    'SEP': 'September',
    'OCT': 'Oktober',
    'NOV': 'November',
    'DEC': 'Desember'
  }
  for key, value in month_data.items():
    string = re.sub(key, value, string)
  return string

def exception_handler(status_code, error_message):
  return {
    'statusCode': status_code,
    'headers': { 'Content-Type': 'application/json' },
    'body': json.dumps(error_message)
  }

def lambda_handler(event, context):
  try:
    origination = event['queryStringParameters']['from']
    destination = event['queryStringParameters']['to']
    tanggal = event['queryStringParameters']['date']
  except: return exception_handler(400, { 'message': 'Invalid or missing query parameter(s)' })

  params = {
    'origination': origination,
    'destination': destination,
    'tanggal': transform_month(tanggal),
    'adult': '1',
    'infant': '0',
    'submit': 'Cari+%26+Pesan+Tiket'
  }

  try: data = extract_data(extract_source(url, params))
  except: return exception_handler(404, { 'message': 'Unable to fetch data at the moment' })

  return {
    'statusCode': 200,
    'headers': { 'Content-Type': 'application/json' },
    'body': json.dumps(data)
  }
