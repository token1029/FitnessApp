import pytest
from bs4 import BeautifulSoup
from fitnessapp.application import calc_bmi, get_bmi_category


def test_render_bmi_calculation_page(client):
    response = client.get('/bmi_calc')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.h1.string == 'BMI Calculator'

# Test for successful BMI calculation with valid inputs


def test_successful_bmi_calculation(client):
    response = client.post('/bmi_calc', data={
        'weight': '70',
        'height': '1.75'
    })

    assert response.status_code == 200
    bmi = calc_bmi(70, 1.75)
    bmi_category = get_bmi_category(bmi)
    soup = BeautifulSoup(response.data, 'html.parser')
    assert str(bmi) in soup.text
    assert bmi_category in soup.text

# Test for handling invalid weight input


def test_invalid_weight_input(client):
    response = client.post('/bmi_calc', data={
        'weight': 'invalid',
        'height': '1.75'
    })

    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.h1.string == 'BMI Calculator'

    assert 'Invalid Category' in soup.text

# Test for handling invalid height input


def test_invalid_height_input(client):
    response = client.post('/bmi_calc', data={
        'weight': '70',
        'height': 'invalid'
    })
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')

    assert soup.h1.string == 'BMI Calculator'

    assert 'Invalid Category' in soup.text

# Test for handling empty inputs


def test_empty_inputs(client):
    response = client.post('/bmi_calc', data={
        'weight': '',
        'height': ''
    })

    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')

    assert soup.h1.string == 'BMI Calculator'

    assert 'Invalid Category' in soup.text

# Test for BMI calculation with boundary values


def test_bmi_calculation_boundaries(client):

    response = client.post('/bmi_calc', data={
        'weight': '50',
        'height': '1.80'
    })
    bmi = calc_bmi(50, 1.80)
    bmi_category = get_bmi_category(bmi)

    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')

    assert str(bmi) in soup.text
    assert bmi_category in soup.text

    response = client.post('/bmi_calc', data={
        'weight': '70',
        'height': '1.75'
    })
    bmi = calc_bmi(70, 1.75)
    bmi_category = get_bmi_category(bmi)

    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')

    assert str(bmi) in soup.text
    assert bmi_category in soup.text

    response = client.post('/bmi_calc', data={
        'weight': '85',
        'height': '1.75'
    })
    bmi = calc_bmi(85, 1.75)
    bmi_category = get_bmi_category(bmi)

    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')

    assert str(bmi) in soup.text
    assert bmi_category in soup.text
